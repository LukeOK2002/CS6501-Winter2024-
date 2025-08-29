#Write a python program based on the mathematical identity shown to give an approximation to the value of pi
#pi^2 / 6 = 1/1^2 + 1/2^2 + 1/3^2
#Use the first 100 terms to calculate the result and print it out to within 4 decimal places
import math
def approx(length):
    result = 0
    for i in range(1, length):
        result += 1 / i**2
    print(result)
    #To see how close the approximation was
    actual_value = math.pi**2 / 6
    print(actual_value)

approx(100)