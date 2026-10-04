from numpy.random import Generator
import numpy
from typing import NamedTuple
import time
import matplotlib.pyplot as plt
from pathlib import Path

class RACH_simulation_Result(NamedTuple):
    success_probability: float
    delay: float


def cakeisalie_reporduce_RACH_baselinemodel(
                        probability_RACH_p: float,
                        probability_HARQ_g: float,
                        MAX_Msg1_connectTest_N: int,
                        Max_Msg3_connectTest_M: int,
                        intgate1: int,
                        Msg1_sendingPhase_delay1: float,
                        Msg2_failPhase_delay2: float,
                        Msg3_sendingPhase_delay3: float,
                        Msg4_recivePhase_delay4: float,
                        randomNumgate1: Generator | None = None
                        ) -> RACH_simulation_Result:
    
    """
        enter val:
            probability_RACH_p: float,
            probability_HARQ_g: float,
            MAX_Msg1_connectTest_N: int,
            Max_Msg3_connectTest_M: int,
            intgate1: int, the number of the IoT-machines
            Msg1_sendingPhase_delay1: float,
            Msg2_failPhase_delay2: float,
            Msg3_sendingPhase_delay3: float,
            Msg4_recivePhase_delay4: float,
            randomNumgate1: the number of random bit generator

        inner:
            [vector]
            RACH_Machines_connect: 
            RACH_Machines_delay: machines action
            RACH_Machines_ready: machines action - sending preamble (phase in: PRACH)
            RACH_Machines_connectCallingFailure: machines action - meeting crashed (phase in: delay2)
            RACH_Machines_connectSucceed: machines action - succeed in RACH, and be ready to start HARQ (phase in: starting HARQ)
            RACH_Machines_aliveable: machines action - succeed in RACH, and have rights to be counted
            RACH_Machines_intoOmega: machines action - succeed in all phase of RACH

        return:

    """

    if randomNumgate1 is None:
        randomNumgate1 = numpy.random.default_rng()

    RACH_Machines_connect = numpy.zeros(intgate1)
    RACH_Machines_delay = numpy.zeros(intgate1)
    RACH_Machines_ready = numpy.ones(intgate1, bool)

    for _ in range( MAX_Msg1_connectTest_N+1 ):
        RACH_Machines_connectCallingFailure = randomNumgate1.random(intgate1) < probability_RACH_p
        RACH_Machines_delay += numpy.where(RACH_Machines_ready, 
                                           numpy.where(RACH_Machines_connectCallingFailure, 
                                                       Msg1_sendingPhase_delay1 + Msg2_failPhase_delay2, 
                                                       Msg1_sendingPhase_delay1), 
                                           0.0)
        RACH_Machines_connectSucceed = RACH_Machines_ready & ~RACH_Machines_connectCallingFailure
        RACH_Machines_aliveHARQ = numpy.zeros(intgate1)
        RACH_Machines_aliveable = RACH_Machines_connectSucceed.copy()
        RACH_Machines_intoOmega = numpy.zeros(intgate1, bool)

        for i in range(Max_Msg3_connectTest_M + 1):
            RACH_Machines_aliveHARQ += RACH_Machines_aliveable
            RACH_Machines_HARQfailure = randomNumgate1.random(intgate1) < probability_HARQ_g
            RACH_Machines_intoOmega |= RACH_Machines_aliveable & ~RACH_Machines_HARQfailure
            RACH_Machines_aliveable &= RACH_Machines_HARQfailure

        RACH_Machines_delay += numpy.where(RACH_Machines_connectSucceed,
                                           Msg3_sendingPhase_delay3 + RACH_Machines_aliveHARQ * Msg4_recivePhase_delay4,
                                           0.0)
        RACH_Machines_connect += RACH_Machines_intoOmega
        RACH_Machines_ready = (RACH_Machines_ready & RACH_Machines_connectCallingFailure) | (RACH_Machines_connectSucceed & ~RACH_Machines_intoOmega)
        if not  RACH_Machines_ready.any():
            break

    return RACH_simulation_Result(RACH_Machines_connect.sum() / intgate1, 
                                  RACH_Machines_delay[RACH_Machines_connect > 0].mean())

def P_omega(p: float, 
            g: float, 
            N: int = 9, 
            M: int = 4
            ) -> float:

    return 1.0 - (p + (1.0 - p) * g ** (M + 1)) ** (N + 1)


def D_closed(p: float, g: float, N: int = 9, M: int = 4,
             d1: float = 10.5, d2: float = 20.0,
             d3: float = 5.0, d4: float = 6.0) -> float:

    C = p + g ** (M + 1) * (1.0 - p)
    f = 1.0 - (N + 1) * C ** N + N * C ** (N + 1)
    t1 = (d1 + d2) * C / ((1.0 - p) * (1.0 - g ** (M + 1))) * f
    t2 = d4 * (1.0 - (M + 1) * g ** M + M * g ** (M + 1)) / (1.0 - g) * (g * (1.0 - C ** (N + 1)) / (1.0 - g ** (M + 1)))
    t3 = (d3 + M * d4 - d2) * (g ** (M + 1) / (1.0 - g ** (M + 1))) * f
    t4 = (d1 + d3 + d4) * (1.0 - C ** (N + 1))
    return (t1 + t2 + t3 + t4) / P_omega(p, g)


# main() 保护
def main() -> None:

    N = 9
    M = 4
    number_devices = 100_000
    d1, d2, d3, d4 = 10.5, 20.0, 5.0, 6.0
    PS = [0.1, 0.3, 0.5, 0.7, 0.9]
    GS = [0.02, 0.5, 0.8, 0.95]

    #verification grid sweep
    theory = numpy.zeros((len(GS), len(PS)))
    sim = numpy.zeros_like(theory)
    theory_d = numpy.zeros((len(GS), len(PS)))
    sim_d = numpy.zeros_like(theory_d)
    t0 = time.time()
    for i, g in enumerate(GS):
        for j, p in enumerate(PS):
            theory[i, j] = P_omega(p, g)
            theory_d[i, j] = D_closed(p, g, N, M, d1, d2, d3, d4)
            result = cakeisalie_reporduce_RACH_baselinemodel(
                p, g, N, M, number_devices, d1, d2, d3, d4)
            sim[i, j] = result.success_probability
            sim_d[i, j] = result.delay
            print(f"p={p}, g={g}: P theory={theory[i,j]:.4f} MC={sim[i,j]:.4f} "
                  f"|dP|={abs(theory[i,j]-sim[i,j]):.5f} | "
                  f"D theory={theory_d[i,j]:.1f} MC={sim_d[i,j]:.1f} ms")
    print(f"grid sweep finished in {time.time() - t0:.1f}s")

    #draw curve plot

    OUT_DIR = Path(__file__).parent / "images"
    OUT_DIR.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(7.5, 5))
    for i, g in enumerate(GS):
        ax.plot(PS, theory[i], "-", lw=1.6, label=f"g = {g} (closed form)")
        ax.plot(PS, sim[i], "o", ms=5, label=f"g = {g} (Monte Carlo)")

    ax.set_xlabel("Collision probability p")
    ax.set_ylabel("Access success probability P(ω)")
    ax.set_title(f"Closed form vs Monte Carlo (N={N+1}, M={M+1}, "
                 f"n_dev={number_devices:,})")
    
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig_grid_curves.png", dpi=160)
    plt.close(fig)

    #average access delay curves (Fig. 5 style)
    fig, ax = plt.subplots(figsize=(7.5, 5))
    for i, g in enumerate(GS):
        ax.plot(PS, theory_d[i], "-", lw=1.6, label=f"g = {g} (closed form)")
        ax.plot(PS, sim_d[i], "s", ms=5, label=f"g = {g} (Monte Carlo)")
    ax.set_xlabel("Collision probability p")
    ax.set_ylabel("Average access delay D, ms")
    ax.set_title(f"Average access delay: closed form vs Monte Carlo "
                 f"(N={N+1}, M={M+1}, n_dev={number_devices:,})")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig_delay_curves.png", dpi=160)
    plt.show()
    print("figures saved: fig_grid_curves.png, fig_delay_curves.png")


# main() 保护
if __name__ == "__main__":
    main()

