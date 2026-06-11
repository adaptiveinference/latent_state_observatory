# CHECK_TOKEN: PYC022

# Define function factorial using a loop
def factorial(n):
    """
    Calculate the factorial of a given integer n using a loop.

    Args:
        n (int): The integer to calculate the factorial of.

    Returns:
        int: The factorial of n.
    """
    # Initialize a variable to store the factorial
    factorial = 1

    # Use a loop to iterate from 1 to n
    for i in range(1, n+1):
        # Multiply the current value of factorial by i
        factorial *= i

    # Return the factorial
    return factorial

# Test the factorial function
print(factorial(5))  # Output: 120
print(factorial(0))  # Output: 1
print(factorial(-1))  # Output: 1
print(factorial(10))  # Output: 3628800
print(factorial(100))  # Output: 36288000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000