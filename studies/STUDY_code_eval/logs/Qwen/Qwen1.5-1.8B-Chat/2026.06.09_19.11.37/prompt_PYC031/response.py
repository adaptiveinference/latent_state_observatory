# CHECK_TOKEN: PYC031

# Define function flatten(list_of_lists)
def flatten(list_of_lists):
    """
    Flatten a list of lists into a single list.

    Args:
        list_of_lists (list): A list of lists containing nested lists.

    Returns:
        list: A single list containing all the elements from the nested lists in the input list.
    """
    flattened_list = []
    for sublist in list_of_lists:
        for element in sublist:
            flattened_list.append(element)
    return flattened_list

# Test the function
nested_list = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print(flatten(nested_list))  # Output: [1, 2, 3, 4, 5, 6, 7, 8, 9]

# Example usage
nested_list2 = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]
print(flatten(nested_list2))  # Output: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]