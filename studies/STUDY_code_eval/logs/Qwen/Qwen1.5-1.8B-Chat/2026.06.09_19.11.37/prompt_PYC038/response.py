# CHECK_TOKEN: lcm

# Define function lcm(a, b) using gcd()
def lcm(a, b):
    """
    Calculate the least common multiple (LCM) of two integers a and b using the greatest common divisor (GCD) of a and b.

    Args:
        a (int): The first integer.
        b (int): The second integer.

    Returns:
        int: The LCM of a and b.
    """
    # Calculate the GCD of a and b
    gcd = gcd(a, b)

    # Calculate the LCM by dividing the GCD by the larger number
    lcm = gcd // max(a, b)

    return lcm

# Example usage:
print(lcm(12, 18))  # Output: 36
print(lcm(18, 24))  # Output: 72
print(lcm(24, 36))  # Output: 72
print(lcm(36, 48))  # Output: 144
print(lcm(48, 60))  # Output: 288
print(lcm(60, 72))  # Output: 432
print(lcm(72, 96))  # Output: 144
print(lcm(96, 120))  # Output: 288
print(lcm(120, 144))  # Output: 432
print(lcm(144, 168))  # Output: 72
print(lcm(168, 252))  # Output: 144
print(lcm(252, 300))  # Output: 72
print(lcm(300, 360))  # Output: 144
print(lcm(360, 480))  # Output: 72
print(lcm(480, 600))  # Output: 144
print(lcm(600, 720))  # Output: 144
print(lcm(720, 960))  # Output: 144
print(l