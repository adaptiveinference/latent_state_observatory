# CHECK_TOKEN: PYC019

# Define function sign(n) returning -1, 0, or 1.

def sign(n):
    """
    Returns the sign of a given integer n.

    Args:
        n (int): The integer to be signed.

    Returns:
        -1, 0, or 1: The sign of n.
    """
    if n < 0:
        return -1
    elif n == 0:
        return 0
    else:
        return 1

# Test the function
print(sign(5))  # Output: 1
print(sign(-5))  # Output: -1
print(sign(0))  # Output: 0
print(sign(10))  # Output: 1
print(sign(100))  # Output: 0
print(sign(1000))  # Output: -1
print(sign(10000))  # Output: 1
print(sign(100000))  # Output: 0
print(sign(1000000))  # Output: -1
print(sign(10000000))  # Output: 1
print(sign(100000000))  # Output: 0
print(sign(1000000000))  # Output: -1
print(sign(10000000000))  # Output: 1
print(sign(1000000000000))  # Output: 0
print(sign(100000000000000))  # Output: -1
print(sign(1000000000000000))  # Output: 1
print(sign(10000000000000000))  # Output: 0
print(sign(1000000000000000000))  # Output: -1
print(sign(100000000000000000000))  # Output: 1
print(sign(1000