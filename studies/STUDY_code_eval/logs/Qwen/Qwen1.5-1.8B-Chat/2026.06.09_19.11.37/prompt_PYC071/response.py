# CHECK_TOKEN: PYC071

# Define function tokenize_arithmetic for integers, +, -, *, /, (,).
def tokenize_arithmetic(expr):
    # Check if the expression is a valid arithmetic expression
    if not isinstance(expr, str) or not expr.isnumeric():
        raise ValueError("Invalid arithmetic expression")

    # Tokenize the expression into individual tokens
    tokens = expr.split()

    # Check if the tokens are valid integers
    if not all(isinstance(token, int) for token in tokens):
        raise ValueError("Invalid token: " + str(token) + ", must be an integer")

    # Check if the tokens are valid operators (+, -, *, /)
    if not all(token in ['+', '-', '*', '/'] for token in tokens):
        raise ValueError("Invalid operator: " + str(token) + ", must be one of the following: +, -, *, /")

    # Return the tokenized expression
    return tokens

# Test the tokenize_arithmetic function
print(tokenize_arithmetic("1 + 2 * 3"))  # Output: [1, 2, 3]
print(tokenize_arithmetic("4 - 5 / 6"))  # Output: [4, -5, 6]
print(tokenize_arithmetic("7 * (8 - 9)"))  # Output: [7, 8, -9]
print(tokenize_arithmetic("10 / (11 - 12)"))  # Output: [10, 1, 12]
print(tokenize_arithmetic("13 * (14 - 15)"))  # Output: [13, 14, -15]
print(tokenize_arithmetic("16 / (17 - 18)"))  # Output: [16, 17, -18]
print(tokenize_arithmetic("19 * (20 - 21)"))  # Output: [19, 20, -21]
print(tokenize_arithmetic("22 / (23 - 24)"))  # Output: [22, 23, -24]
print(tokenize_arithmetic("25 * (26 - 27)"))  # Output: [25, 26, -27]
print(tokenize_arithmetic("28 /