from numpy.random import Generator, default_rng
import numpy

def simulation1_in_RACH(probability_RACH_p: float,
                        probability_HARQ_g: float,
                        MAX_Msg1_connectTest_N: int,
                        Max_Msg3_connectTest_M: int,
                        randomNumgate1: Generator | None = None
                        ) -> bool:
    """
        inner val:  propbability_RACH_p: float,
                    propbability_HARQ_g: float,
                    MAX_Msg1_connetTest_N: int,
                    Max_Msg3_connetTest_M: int,
                    randomNumgate2: Generator
         
        Msg1_failed_times: int (Msg3_failed_times < Max_Msg1_connetTest_N)
        Msg3_failed_times: int (Msg3_failed_times < Max_Msg3_connetTest_M)
                    
        return funcOut1
        funcOut1: result of RACH (true: RACH succeeded! | false: RACH failed…)
    """

    Msg3_failed_times = 0 #free value?

    if randomNumgate1 is None:
        randomNumgate1 = default_rng()
    
    for _ in range(MAX_Msg1_connectTest_N + 1):
        if randomNumgate1.random() < probability_RACH_p:
            continue
        for _ in range(Max_Msg3_connectTest_M + 1):
            if randomNumgate1.random() < probability_HARQ_g:
                Msg3_failed_times += 1
            else:
                return True

    return False

#main() 保护
def main() -> None:

    p = 0.6
    g = 0.02
    N = 9
    M = 4
    repeatting_times = 50000

    print(
        "at the N=",N+1,"M = ", M+1,"and repeat in", repeatting_times ,"\n",
          "the simulation of RACH succeeded probabiliy result: ",
          numpy.mean([simulation1_in_RACH(p, g, N, M)
                      for _ in range(repeatting_times)])
        )
          

#main() 保护
if  __name__ == "__main__":
    main()
