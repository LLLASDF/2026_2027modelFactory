import numpy

#Globle in here
#伪随机数default_rng()
rng = numpy.random.default_rng() 

p = 0.4 #Msg1 Crash probability
test_of_times = 30000


def count_fail_times(intgate1: int, 
                    floatgate1: float
                    ) -> int:
    """
        function:counting the how many "fail” of times

        inner val: intgate1,
                   floatgate1

        local function val: intout1

        intgate1 = test_of_times
        floatgate1 = p (the probability of Msg1 crashed)

        return = intout1 = failed times
    """
    #boundLocal val: intout1
    intout1 = 0

    for _ in range(intgate1):
        if rng.random() < floatgate1: 
            #Msg1 sending fail - Crash
            intout1 += 1 

    return intout1


def calcOfSuccess_Proportion(intgate1 :int, 
                            intgate2 :int
                            ) -> float:
    """  
        function:counting the how many "fail" of times

        inner val: intgate1, intgate2
        intgate1 = test_of_times
        intgate2 = failed_times

        return = floatout = success_proportion
    """

    #入口校验三件套：isinstance → 取值范围 → raise
    if not isinstance(intgate1, int) or not isinstance(intgate2, int):
        raise TypeError("worng input type")
    if intgate1 <= 0:
        raise ValueError("input must greater than 0")
    if not 0 <= intgate2 <= intgate1:
        raise ValueError("input have a wron interval")
    else:
        floatout1 :float = 1 - (intgate2 / intgate1)
        return floatout1

#main() 保护
def main() -> None:
    failed_times = count_fail_times(test_of_times, p)
    print("report:\n",
          "at the times of testing", test_of_times, "\n"
          "and the crash probability", p, "\n"
          "the proportion of success = ", calcOfSuccess_Proportion(test_of_times, failed_times)
          )
    
#main() 保护
if  __name__ == "__main__":
    main()