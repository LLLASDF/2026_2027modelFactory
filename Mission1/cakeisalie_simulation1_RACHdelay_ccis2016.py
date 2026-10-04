from numpy.random import Generator, default_rng
import numpy
from collections.abc import Sequence
from typing import NamedTuple
import time

class RACH_Result(NamedTuple):
    success: bool
    n: int
    m: int
    k: int

def simulation1_in_RACH(probability_RACH_p: float,
                        probability_HARQ_g: float,
                        MAX_Msg1_connectTest_N: int,
                        Max_Msg3_connectTest_M: int,
                        randomNumgate1: Generator | None = None,
                        ) -> RACH_Result:
    """
        inner val:  propbability_RACH_p: float,
                    propbability_HARQ_g: float,
                    MAX_Msg1_connetTest_N: int,
                    Max_Msg3_connetTest_M: int,
                    randomNumgate2: Generator
         
        Msg1_failed_times: int (Msg3_failed_times < Max_Msg1_connetTest_N)
        Msg3_failed_times: int (Msg3_failed_times < Max_Msg3_connetTest_M)
                    
        return tuple[funcOut1: bool; Msg1_failed_times: int; Msg3_failed_times: int]
        funcOut1: result of RACH (true: RACH succeeded! | false: RACH failed…)
        Msg1_sendingTest_times: n
        Msg3_failed_times: m
        Msg1_failed_times: k
    """

    Msg3_fullfailed_times = 0   #k

    if randomNumgate1 is None:
        randomNumgate1 = default_rng()
    
    for Msg1_sendingTest_times in range(MAX_Msg1_connectTest_N + 1):     
        if randomNumgate1.random() < probability_RACH_p:
            continue
        Msg3_failed_times = 0
        for Msg3_failed_times in range(Max_Msg3_connectTest_M + 1):
            if randomNumgate1.random() < probability_HARQ_g:
                Msg3_failed_times += 1
            else:
                return RACH_Result(True, 
                                   Msg1_sendingTest_times, 
                                   Msg3_failed_times, 
                                   Msg3_fullfailed_times)
            
        Msg3_fullfailed_times += 1
    
    return RACH_Result(False,  
                       Msg1_sendingTest_times, 
                       0, 
                       Msg3_fullfailed_times)

def simulation_RACH_delay(funcTupleGate1: Sequence[tuple[bool, int, int, int]],
                          Max_Msg3_connectTest_M: int,
                          Msg1_sendingPhase_delay1: float,
                          Msg2_failPhase_delay2: float,
                          Msg3_sendingPhase_delay3: float,
                          Msg4_recivePhase_delay4: float
                          ) -> tuple[float, float]:
    """
        inner val:
        arrayTupleGate1: array-float
        signa_in_loop1: int

        return:
        funcOut1: RACH succeeded probabiliy result
        funcOut2: succeeded RACH delay result
    """

    arrayTupleGate1 = numpy.array(funcTupleGate1, dtype=float)

    succeed, n, m, k = arrayTupleGate1.T
    funcOut1:float = numpy.mean(succeed)
    delay = []

    for succeed_i, n_i, m_i, k_i in zip(succeed, n, m, k):
        if not succeed_i:
            continue
        delay_i = (n_i - k_i) * (Msg1_sendingPhase_delay1 + Msg2_failPhase_delay2) + k_i*(Msg1_sendingPhase_delay1 + Msg3_sendingPhase_delay3 + Max_Msg3_connectTest_M * Msg4_recivePhase_delay4) + Msg1_sendingPhase_delay1 + Msg3_sendingPhase_delay3 + (m_i + 1) * Msg4_recivePhase_delay4
        delay.append(delay_i)

    funcOut2 = float( numpy.mean(delay) )

    return funcOut1, funcOut2

 

#main() 保护
def main() -> None:

    p = 0.6
    g1 = 0.02
    N = 9
    M = 4
    repeating_times = 100000

    Sequ_results = [simulation1_in_RACH(p, g1, N, M) for _ in range(repeating_times)]
    k_greater0_ratio = sum(1 for r in Sequ_results if r.k > 0) / len(Sequ_results)
    Tup_result = simulation_RACH_delay(Sequ_results, M, 10.5, 20.0, 5.0, 6.0)

    print(f"at the N = {N+1} M = {M+1} and repeat in {repeating_times }\nthe simulation of RACH succeeded probabiliy result: {Tup_result[0]*100:.4f}%\nthe simulation of the delay is: {Tup_result[1]:.2f}ms\nand the ratio of k (k>0): {k_greater0_ratio*100:.2f}%")
    print(time)
    
#main() 保护
if  __name__ == "__main__":
    main()