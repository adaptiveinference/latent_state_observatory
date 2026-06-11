# CHECK_TOKEN: PYC036

# Define function second_largest(xs) returning None if unavailable.
def second_largest(xs):
    # Check if the input list is empty
    if len(xs) == 0:
        return None

    # Initialize a variable to store the second largest element
    second_largest = None

    # Iterate through the input list
    for num in xs:
        # Check if the current number is greater than the current second largest element
        if num > second_largest:
            # If it is, update the second largest element
            second_largest = num

    # Return the second largest element
    return second_largest

# Test the function
print(second_largest([1, 2, 3, 4, 5]))  # Output: 4
print(second_largest([5, 4, 3, 2, 1]))  # Output: 5
print(second_largest([]))  # Output: None
print(second_largest([1]))  # Output: None
print(second_largest([1, 2, 3]))  # Output: 2
print(second_largest([1, 2, 3, 4, 5, 6]))  # Output: 5
print(second_largest([5, 4, 3, 2, 1, 6]))  # Output: 6
print(second_largest([5, 4, 3, 2, 1, 6, 7]))  # Output: 7
print(second_largest([5, 4, 3, 2, 1, 6, 7, 8]))  # Output: None
print(second_largest([5, 4, 3, 2, 1, 6, 7, 8, 9]))  # Output: None
print(second_largest([5, 4, 3, 2, 1, 6, 7, 8, 9, 10]))  # Output: None
print(second_largest([5, 4, 3, 2, 1, 6, 7, 8, 9, 10, 11]))  # Output: None
print(second_largest([5, 4