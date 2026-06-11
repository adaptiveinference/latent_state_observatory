# CHECK_TOKEN: PYC021

# Define function sum_to_n(n) returning 1+...+n using a loop.

def sum_to_n(n):
    """
    This function takes an integer n as input and returns the sum of the numbers from 1 to n using a loop.

    Parameters:
    n (int): The integer value for which the sum needs to be calculated.

    Returns:
    int: The sum of the numbers from 1 to n.
    """
    # Initialize a variable to store the sum
    total_sum = 0

    # Iterate from 1 to n (inclusive)
    for i in range(1, n+1):
        # Add the current number to the total sum
        total_sum += i

    # Return the final sum
    return total_sum

# Test the function
print(sum_to_n(5))  # Output: 15
print(sum_to_n(10))  # Output: 55
print(sum_to_n(15))  # Output: 90
print(sum_to_n(20))  # Output: 140
print(sum_to_n(25))  # Output: 195
print(sum_to_n(30))  # Output: 240
print(sum_to_n(35))  # Output: 305
print(sum_to_n(40))  # Output: 360
print(sum_to_n(45))  # Output: 420
print(sum_to_n(50))  # Output: 480
print(sum_to_n(55))  # Output: 545
print(sum_to_n(60))  # Output: 600
print(sum_to_n(65))  # Output: 655
print(sum_to_n(70))  # Output: 705
print(sum_to_n(75))  # Output: 750
print(sum_to_n(80))  # Output: 800
print(sum_to_n(85))  # Output: 850
print(sum_to_n(90))  # Output: 900
print(sum_to_n(95))  # Output: 950
print(sum_to_n(1