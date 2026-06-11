# CHECK_TOKEN: PYC028

# Define function filter_positive(xs) returning a new list.
def filter_positive(xs):
    """
    Returns a new list containing only the positive numbers from the input list xs.

    Args:
        xs (list): A list of numbers.

    Returns:
        list: A new list containing only the positive numbers from the input list xs.
    """
    # Check if the input list is empty
    if not xs:
        return []

    # Initialize an empty list to store the positive numbers
    positive_numbers = []

    # Iterate through each number in the input list
    for num in xs:
        # Check if the number is positive
        if num > 0:
            # If the number is positive, add it to the positive_numbers list
            positive_numbers.append(num)

    # Return the new list containing only the positive numbers
    return positive_numbers

# Test the function with a sample input list
sample_input_list = [1, -2, 3, -4, 5, -6, 7, -8, 9]
print(filter_positive(sample_input_list))  # Output: [1, 3, 5, 7, 9]

# Example usage
input_list = [1, -2, 3, -4, 5, -6, 7, -8, 9]
print(filter_positive(input_list))  # Output: [1, 3, 5, 7, 9]