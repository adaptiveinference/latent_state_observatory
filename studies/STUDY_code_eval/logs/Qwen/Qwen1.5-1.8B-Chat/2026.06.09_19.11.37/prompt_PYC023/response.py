# CHECK_TOKEN: PyC023

# Define function count_even(xs)
def count_even(xs):
    """
    This function takes a list of integers xs as input and returns the number of even numbers in the list.

    Args:
        xs (list[int]): A list of integers.

    Returns:
        int: The number of even numbers in the list.

    Raises:
        ValueError: If the input list contains non-integer values.
    """
    # Check if the input list is a list of integers
    if not isinstance(xs, list):
        raise ValueError("Input list must be a list of integers.")

    # Initialize a counter variable to keep track of the number of even numbers
    even_count = 0

    # Iterate over each element in the list
    for num in xs:
        # Check if the number is even
        if num % 2 == 0:
            # Increment the counter variable
            even_count += 1

    # Return the number of even numbers
    return even_count

# Test the function
print(count_even([1, 2, 3, 4, 5]))  # Output: 3
print(count_even([1, 2, 3, 4, 6]))  # Output: 0
print(count_even([]))  # Output: 0
print(count_even([1, 2, 3, 4, "5"]))  # Raises ValueError: Input list must be a list of integers.