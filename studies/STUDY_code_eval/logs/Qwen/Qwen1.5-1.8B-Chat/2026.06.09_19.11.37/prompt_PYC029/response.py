# CHECK_TOKEN: squares

# Define function squares(xs) returning list of squares.
def squares(xs):
    """
    Returns a list of squares of the input list xs.

    Args:
        xs (list): A list of integers.

    Returns:
        list: A list of the squares of the input list xs.
    """
    return [x**2 for x in xs]  # Implement the squaring function using list comprehension

# Test the function
print(squares([1, 2, 3]))  # Output: [1, 4, 9]
print(squares([5, 6, 7]))  # Output: [25, 36, 49]
print(squares([8, 9, 10]))  # Output: [64, 81, 100]