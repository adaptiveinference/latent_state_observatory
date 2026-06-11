# CHECK_TOKEN: PYC054

# Define a generator function countdown(n)
def countdown(n):
    """
    This function takes an integer n as input and returns a generator that generates the numbers from 1 to n in reverse order.
    """
    # Initialize an empty list to store the generated numbers
    numbers = []

    # Iterate from n down to 1
    for i in range(n, 0, -1):
        # Append the current number to the list
        numbers.append(i)

    # Return the generator
    return numbers

# Test the countdown function
print(countdown(5))  # Output: [5, 4, 3, 2, 1]
print(countdown(10))  # Output: [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
print(countdown(15))  # Output: [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]