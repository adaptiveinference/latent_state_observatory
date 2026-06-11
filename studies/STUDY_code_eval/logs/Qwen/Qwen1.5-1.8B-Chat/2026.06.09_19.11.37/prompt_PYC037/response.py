# CHECK_TOKEN: gcd

# Function to calculate the greatest common divisor (GCD) of two integers using the Euclidean algorithm
def gcd(a, b):
    """
    Calculate the greatest common divisor (GCD) of two integers using the Euclidean algorithm.

    Args:
        a (int): The first integer to be divided.
        b (int): The second integer to be divided.

    Returns:
        int: The GCD of a and b.
    """
    # Base case: if b is 0, return a as the GCD
    if b == 0:
        return a

    # Recursive case: calculate the GCD of b and the remainder of a divided by b
    return gcd(b, a % b)

# Example usage:
print(gcd(12, 18))  # Output: 6
print(gcd(17, 23))  # Output: 1
print(gcd(10, 20))  # Output: 10
print(gcd(21, 28))  # Output: 7
print(gcd(15, 30))  # Output: 15
print(gcd(31, 36))  # Output: 13
print(gcd(1, 2))  # Output: 1
print(gcd(2, 3))  # Output: 1
print(gcd(3, 4))  # Output: 1
print(gcd(4, 5))  # Output: 1
print(gcd(5, 6))  # Output: 1
print(gcd(6, 7))  # Output: 1
print(gcd(7, 8))  # Output: 1
print(gcd(8, 9))  # Output: 1
print(gcd(9, 10))  # Output: 1
print(gcd(11, 12))  # Output: 1
print(gcd(12, 13))  # Output: 1
print(gcd(13, 14))  # Output: 1
print(gcd(14, 15))  # Output: 1
print(gcd(15, 16))  #