import math as mt
print("PyCalc : A Simple and Lightweight Calculator. Made in Python!")
print()
print("Select a Mathematical Operation : ")
print()
print("1. Addition")
print("2. Subtraction")
print("3. Multiplication")
print("4. Division")
print("5. Exponents (x^y)")
print("6. Square Root")
print("7. Cube Root")
print("8. Approximate / Rounding")
print("9. Heron's Formula")
print("10. Simple Interest")
print("11. Compound Interest")
print("12. Exit Program")
while True:
    print()
    ch = input("Enter choice [ 1 - 12 ] : ")
    print()
    if ch in ('1', '2', '3', '4' , '5' , '6' , '7' , '8', '9', '10', '11', '12'):
        if ch == '1':
            x = float(input("Enter first number : "))
            y = float(input("Enter second number : "))
            print(x, "+" , y, "=", (x + y))

        elif ch == '2':
            x = float(input("Enter first number : "))
            y = float(input("Enter second number : "))
            print(x, "-", y, "=", (x - y))

        elif ch == '3':
            x = float(input("Enter first number : "))
            y = float(input("Enter second number : "))
            print(x, "*", y, "=", (x * y))

        elif ch == '4':
            x = float(input("Enter first number : "))
            y = float(input("Enter second number : "))
            print(x, "/", y, "=", (x / y))
        elif ch == '5':
            x = float(input("Enter first number : "))
            y = float(input("Enter second number : "))
            print(x, "^", y, "=", mt.pow(x, y))
        elif ch == '6':
            x = float(input("Enter a number : "))
            print("Root x = " , mt.sqrt(x))
        elif ch == '7':
            x = float(input("Enter a number : "))
            print("C. Root x = " , mt.cbrt(x))
        elif ch == '8' :
            x = float(input("Enter a number : "))
            print(round(x))
        elif ch == '9':
            print("NOTE: Some Calculations may print 0.0 depending on the values!")
            print()
            a = float(input("Enter the first side [a] : "))
            b = float(input("Enter the second side [b] : "))
            c = float(input("Enter third side [c] : "))
            s = a+b+c
            print("Perimeter =" , s)
            s /= 2
            print("s = " , s)
            ar = float(mt.sqrt(s*(s-a)*(s-b)*(s-c)))
            print("Area = ", ar)
        elif ch == '10' :
            p = float(input("Enter the Principal : "))
            r = float(input("Enter the Rate [ as a percentage, ex : 10 for 10% ] : "))
            t = float(input("Enter the Time [ Years ] : "))
            si: float = p*r*t
            si /= 100
            print("Simple Interest", si)
            print("Amount = " , (si+p))
        elif ch == '11':
            print("Compound Interest Calculation")
            print()
            p = float(input("Enter the Principal : "))
            r = float(input("Enter the Rate [ as a percentage, ex : 10 for 10% ] : "))
            n = float(input("Enter the number of times interest is compounded per year: "))
            t = float(input("Enter the Time [ Years ] : "))
            x = (100+r)/100
            a = p*mt.pow(((100+r)/100),(n*t))
            ci = a - p
            print("Compound Interest =", ci)
            print("Amount = " , a)
        elif ch == '12' :
            print()
            print("Exiting Program....")
            exit(0)
        next_calc = input("Do you want to do another calculation? (y/n): ")
        if next_calc == "n" or next_calc == "N" or next_calc == "No" or next_calc == "no" :
            break
    else :
        print("Please enter a Valid Input! Restarting the Program...")