# CHECK_TOKEN: PYC009

# Define function list_len(xs) returning len(xs)
def list_len(xs):
    """
    Returns the length of the list xs.

    Args:
        xs (list): A list of integers.

    Returns:
        int: The length of the list xs.
    """
    return len(xs)

# Test the function
print(list_len([1, 2, 3, 4, 5]))  # Output: 5
print(list_len([6, 7, 8, 9, 10]))  # Output: 5
print(list_len([]))  # Output: 0
print(list_len([1, 2, 3, 4, 5, 6]))  # Output: 6
print(list_len([1, 2, 3, 4, 5, 6, 7]))  # Output: 7
print(list_len([1, 2, 3, 4, 5, 6, 7, 8]))  # Output: 8
print(list_len([1, 2, 3, 4, 5, 6, 7, 8, 9]))  # Output: 9
print(list_len([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))  # Output: 9
print(list_len([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]))  # Output: 10
print(list_len([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]))  # Output: 11
print(list_len([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]))  # Output: 12
print(list_len([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12