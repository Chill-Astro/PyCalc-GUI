import customtkinter
import os
import math as mt

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

root = customtkinter.CTk()
root.geometry("950x650")
root.title("PyCalc GUI - Portable")
root.resizable(False, False) # Disable window resizing
icon_path = os.path.join(".", "Pycalc.ico")  # Construct the file path
root.iconbitmap("Pycalc.ico")  # Set the title bar icon
# Sidebar Frame
sidebar_frame = customtkinter.CTkFrame(root, width=150, corner_radius=0)
sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
sidebar_frame.grid_rowconfigure(13, weight=1) # Adjusted row configure

# Home Button (Before Addition)
button_home = customtkinter.CTkButton(sidebar_frame, text="Home", command=lambda: show_home_text())
button_home.grid(row=1, column=0, padx=20, pady=10)

# Operation Buttons (in Sidebar) - Shifted down by one row
button_addition = customtkinter.CTkButton(sidebar_frame, text="Addition", command=lambda: change_operation("Addition"))
button_addition.grid(row=2, column=0, padx=20, pady=10)

button_subtraction = customtkinter.CTkButton(sidebar_frame, text="Subtraction", command=lambda: change_operation("Subtraction"))
button_subtraction.grid(row=3, column=0, padx=20, pady=10)

button_multiplication = customtkinter.CTkButton(sidebar_frame, text="Multiplication", command=lambda: change_operation("Multiplication"))
button_multiplication.grid(row=4, column=0, padx=20, pady=10)

button_division = customtkinter.CTkButton(sidebar_frame, text="Division", command=lambda: change_operation("Division"))
button_division.grid(row=5, column=0, padx=20, pady=10)

button_exponentiation = customtkinter.CTkButton(sidebar_frame, text="Exponentiation", command=lambda: change_operation("Exponentiation"))
button_exponentiation.grid(row=6, column=0, padx=20, pady=10)

button_square_root = customtkinter.CTkButton(sidebar_frame, text="Square Root", command=lambda: change_operation("Square Root"))
button_square_root.grid(row=7, column=0, padx=20, pady=10)

button_cube_root = customtkinter.CTkButton(sidebar_frame, text="Cube Root", command=lambda: change_operation("Cube Root"))
button_cube_root.grid(row=8, column=0, padx=20, pady=10)

button_rounding = customtkinter.CTkButton(sidebar_frame, text="Rounding", command=lambda: change_operation("Rounding"))
button_rounding.grid(row=9, column=0, padx=20, pady=10)

button_herons_formula = customtkinter.CTkButton(sidebar_frame, text="Heron's Formula", command=lambda: change_operation("Heron's Formula"))
button_herons_formula.grid(row=10, column=0, padx=20, pady=10)

button_simple_interest = customtkinter.CTkButton(sidebar_frame, text="Simple Interest", command=lambda: change_operation("Simple Interest"))
button_simple_interest.grid(row=11, column=0, padx=20, pady=10)

button_compound_interest = customtkinter.CTkButton(sidebar_frame, text="Compound Interest", command=lambda: change_operation("Compound Interest"))
button_compound_interest.grid(row=12, column=0, padx=20, pady=10)

button_exit = customtkinter.CTkButton(sidebar_frame, text="Exit", command=root.destroy)
button_exit.grid(row=13, column=0, padx=20, pady=10)


# Main Frame (Right side)
main_frame = customtkinter.CTkFrame(root, corner_radius=0)
main_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=10) # Reduced padx here!
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

# Guide Title Label (in Main Frame)
guide_title_label = customtkinter.CTkLabel(main_frame, text="Operation Guide", font=customtkinter.CTkFont(size=24, weight="bold"))
guide_title_label.pack(pady=20)

# Formula/Example Label (in Main Frame) - Will be updated
formula_label = customtkinter.CTkLabel(main_frame, text="", wraplength=400, justify="left")
formula_label.pack(pady=10)

# Input Widgets Frame (in Main Frame) - Will be dynamically populated
input_frame = customtkinter.CTkFrame(main_frame)
input_frame.pack(pady=20, fill="x", expand=True)

# Result Label (in Main Frame) - Will display calculation results
result_label = customtkinter.CTkLabel(main_frame, text="", font=customtkinter.CTkFont(size=16, weight="bold"))
result_label.pack(pady=20)


# Global variables
entry_first_num = None
entry_second_num = None
entry_third_num = None
entry_rate = None
entry_time = None
entry_n_compound = None
current_operation = None


def clear_input_frame():
    for widget in input_frame.winfo_children():
        widget.destroy()

def calculate_result():
    global current_operation, entry_first_num, entry_second_num, entry_third_num, entry_rate, entry_time, entry_n_compound

    try:
        if current_operation == "Addition":
            num1 = float(entry_first_num.get())
            num2 = float(entry_second_num.get())
            result = num1 + num2
            result_label.configure(text=f"Result: {result}")

        elif current_operation == "Subtraction":
            num1 = float(entry_first_num.get())
            num2 = float(entry_second_num.get())
            result = num1 - num2
            result_label.configure(text=f"Result: {result}")

        elif current_operation == "Multiplication":
            num1 = float(entry_first_num.get())
            num2 = float(entry_second_num.get())
            result = num1 * num2
            result_label.configure(text=f"Result: {result}")

        elif current_operation == "Division":
            num1 = float(entry_first_num.get())
            num2 = float(entry_second_num.get())
            if num2 == 0:
                result_label.configure(text="Error: Division by zero!")
            else:
                result = num1 / num2
                result_label.configure(text=f"Result: {result}")

        elif current_operation == "Exponentiation":
            num1 = float(entry_first_num.get())
            num2 = float(entry_second_num.get())
            result = mt.pow(num1, num2)
            result_label.configure(text=f"Result: {result}")

        elif current_operation == "Square Root":
            num1 = float(entry_first_num.get())
            if num1 < 0:
                result_label.configure(text="Error: Invalid input for square root (negative number)!")
            else:
                result = mt.sqrt(num1)
                result_label.configure(text=f"Result: {result}")

        elif current_operation == "Cube Root":
            num1 = float(entry_first_num.get())
            result = mt.cbrt(num1)
            result_label.configure(text=f"Result: {result}")

        elif current_operation == "Rounding":
            num1 = float(entry_first_num.get())
            result = round(num1)
            result_label.configure(text=f"Result: {result}")

        elif current_operation == "Heron's Formula":
            a = float(entry_first_num.get())
            b = float(entry_second_num.get())
            c = float(entry_third_num.get())
            s = (a + b + c) / 2
            if s <= a or s <= b or s <= c:
                result_label.configure(text="Error: Invalid sides, triangle inequality not satisfied or side is zero.")
            elif a <= 0 or b <= 0 or c <= 0:
                result_label.configure(text="Error: Sides must be positive values.")
            else:
                area = mt.sqrt(s * (s - a) * (s - b) * (s - c))
                result_label.configure(text=f"Area: {area}")

        elif current_operation == "Simple Interest":
            p = float(entry_first_num.get())
            r = float(entry_rate.get())
            t = float(entry_time.get())
            si = (p * r * t) / 100
            amount = si + p
            result_label.configure(text=f"Simple Interest: {si:.2f}\nAmount: {amount:.2f}")

        elif current_operation == "Compound Interest":
            p = float(entry_first_num.get())
            r = float(entry_rate.get())
            n = float(entry_n_compound.get())
            t = float(entry_time.get())

            if r <= -100:
                result_label.configure(text="Error: Rate must be greater than -100%.")
            elif n <= 0 or t <= 0:
                result_label.configure(text="Error: Compounding frequency and Time must be positive values.")
            else:
                amount = p * mt.pow((1 + (r / 100) / n), (n * t))
                ci = amount - p
                result_label.configure(text=f"Compound Interest: {ci:.2f}\nAmount: {amount:.2f}")


    except ValueError:
        result_label.configure(text="Invalid input. Please enter numbers.")
    except Exception as e:
        result_label.configure(text=f"An error occurred: {e}")


def change_operation(operation):
    global current_operation, entry_first_num, entry_second_num, entry_third_num, entry_rate, entry_time, entry_n_compound
    current_operation = operation
    guide_title_label.configure(text=f"{operation} Guide")
    result_label.configure(text="")

    clear_input_frame()

    if operation == "Addition":
        formula_label.configure(text="Formula: A + B") # Removed Example!
        entry_first_num = customtkinter.CTkEntry(input_frame, placeholder_text="Enter first number")
        entry_first_num.pack(pady=10, fill="x")
        entry_second_num = customtkinter.CTkEntry(input_frame, placeholder_text="Enter second number")
        entry_second_num.pack(pady=10, fill="x")

    elif operation == "Subtraction":
        formula_label.configure(text="Formula: A - B") # Removed Example!
        entry_first_num = customtkinter.CTkEntry(input_frame, placeholder_text="Enter first number")
        entry_first_num.pack(pady=10, fill="x")
        entry_second_num = customtkinter.CTkEntry(input_frame, placeholder_text="Enter second number")
        entry_second_num.pack(pady=10, fill="x")

    elif operation == "Multiplication":
        formula_label.configure(text="Formula: A * B") # Removed Example!
        entry_first_num = customtkinter.CTkEntry(input_frame, placeholder_text="Enter first number")
        entry_first_num.pack(pady=10, fill="x")
        entry_second_num = customtkinter.CTkEntry(input_frame, placeholder_text="Enter second number")
        entry_second_num.pack(pady=10, fill="x")

    elif operation == "Division":
        formula_label.configure(text="Formula: A / B") # Removed Example!
        entry_first_num = customtkinter.CTkEntry(input_frame, placeholder_text="Enter first number")
        entry_first_num.pack(pady=10, fill="x")
        entry_second_num = customtkinter.CTkEntry(input_frame, placeholder_text="Enter second number")
        entry_second_num.pack(pady=10, fill="x")

    elif operation == "Exponentiation":
        formula_label.configure(text="Formula: A ^ B") # Removed Example!
        entry_first_num = customtkinter.CTkEntry(input_frame, placeholder_text="Enter base (x)")
        entry_first_num.pack(pady=10, fill="x")
        entry_second_num = customtkinter.CTkEntry(input_frame, placeholder_text="Enter exponent (y)")
        entry_second_num.pack(pady=10, fill="x")

    elif operation == "Square Root":
        formula_label.configure(text="Formula: √x") # Removed Example!
        entry_first_num = customtkinter.CTkEntry(input_frame, placeholder_text="Enter number (x)")
        entry_first_num.pack(pady=10, fill="x")
        entry_second_num = None

    elif operation == "Cube Root":
        formula_label.configure(text="Formula: cbrt(x)") # Removed Example!
        entry_first_num = customtkinter.CTkEntry(input_frame, placeholder_text="Enter number (x)")
        entry_first_num.pack(pady=10, fill="x")
        entry_second_num = None

    elif operation == "Rounding":
        formula_label.configure(text="Formula: round(x)") # Removed Example!
        entry_first_num = customtkinter.CTkEntry(input_frame, placeholder_text="Enter number (x)")
        entry_first_num.pack(pady=10, fill="x")
        entry_second_num = None

    elif operation == "Heron's Formula":
        formula_label.configure(text="Formula: Area = √(s(s-a)(s-b)(s-c)), s = (a+b+c)/2") # Removed Example!
        entry_first_num = customtkinter.CTkEntry(input_frame, placeholder_text="Enter side a")
        entry_first_num.pack(pady=10, fill="x")
        entry_second_num = customtkinter.CTkEntry(input_frame, placeholder_text="Enter side b")
        entry_second_num.pack(pady=10, fill="x")
        entry_third_num = customtkinter.CTkEntry(input_frame, placeholder_text="Enter side c")
        entry_third_num.pack(pady=10, fill="x")

    elif operation == "Simple Interest":
        formula_label.configure(text="Formula: SI = (P*R*T)/100, Amount = SI + P") # Removed Example!
        entry_first_num = customtkinter.CTkEntry(input_frame, placeholder_text="Enter Principal (P)")
        entry_first_num.pack(pady=10, fill="x")
        entry_rate = customtkinter.CTkEntry(input_frame, placeholder_text="Enter Rate (%) (R)")
        entry_rate.pack(pady=10, fill="x")
        entry_time = customtkinter.CTkEntry(input_frame, placeholder_text="Enter Time (Years) (T)")
        entry_time.pack(pady=10, fill="x")
        entry_second_num = None


    elif operation == "Compound Interest":
        formula_label.configure(text="Formula: CI = Amount - P, Amount = P(1 + R/(100*N))^(N*T)") # Removed Example!
        entry_first_num = customtkinter.CTkEntry(input_frame, placeholder_text="Enter Principal (P)")
        entry_first_num.pack(pady=10, fill="x")
        entry_rate = customtkinter.CTkEntry(input_frame, placeholder_text="Enter Rate (%) (R)")
        entry_rate.pack(pady=10, fill="x")
        entry_n_compound = customtkinter.CTkEntry(input_frame, placeholder_text="Compounding Frequency (N)")
        entry_n_compound.pack(pady=10, fill="x")
        entry_time = customtkinter.CTkEntry(input_frame, placeholder_text="Enter Time (Years) (T)")
        entry_time.pack(pady=10, fill="x")
        entry_second_num = None


    calculate_button = customtkinter.CTkButton(input_frame, text="Calculate", command=calculate_result)
    calculate_button.pack(pady=20)

def show_home_text():
    global current_operation
    current_operation = "Home"
    guide_title_label.configure(text="Welcome to PyCalc!")
    result_label.configure(text="")
    clear_input_frame()
    home_text = "PyCalc : A Simple and Lightweight Calculator. Made in Python!\n\n" \
                "Use the sidebar on the left to select a mathematical operation."
    formula_label.configure(text=home_text, justify="center")
# Set default to Home text on startup
show_home_text()
root.mainloop()