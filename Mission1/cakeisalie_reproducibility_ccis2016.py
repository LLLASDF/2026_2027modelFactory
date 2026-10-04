import cakeisalie_simulation_cakeisalie_reporduce_RACH_baselinemodel_ccis2016
import cakeisalie_simulation1_RACHdelay_ccis2016

def P_omega(p: float, 
            g: float, 
            N: int = 9, 
            M: int = 4
            ) -> float:

    return 1.0 - (p + (1.0 - p) * g**(M+1))**(N+1)

#main() 保护
def main() -> None:
    for p in [0.1, 0.3, 0.5, 0.7, 0.9]:
        for g in [0.02, 0.5, 0.8, 0.95]:
            theory = P_omega(p, g)
            sim = cakeisalie_reporduce_RACH_baselinemodel(p, g, 9, 4, 100_000, ...).success_probability
            print(f"p={p}, g={g}: 理论={theory:.4f} 仿真={sim:.4f} 差={abs(theory-sim):.5f}")

#main() 保护
if  __name__ == "__main__":
    main()