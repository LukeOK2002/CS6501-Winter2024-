def main():
    real_number1 = float(input("Enter first number: "))
    real_number2 = float(input("Enter second number: "))

    origin_dist = (((real_number1)**2) + (real_number2)**2)**0.5

    print(f'Distance from point of origin: {origin_dist:.2f}')
main()