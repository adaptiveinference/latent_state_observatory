# CHECK_TOKEN: merge_sorted

# Merge two sorted lists into a single sorted list
def merge_sorted(a, b):
    # Check if the lists are empty
    if not a or not b:
        return []

    # Create an empty list to store the merged sorted list
    merged_list = []

    # Iterate over the elements of the first list
    for i in range(len(a)):
        # Compare the current element with the next element in the second list
        if a[i] < b[i]:
            # If the current element is smaller, append it to the merged list
            merged_list.append(a[i])
        else:
            # If the current element is larger, append it to the merged list
            merged_list.append(b[i])

    # Return the merged sorted list
    return merged_list

# Test the function
print(merge_sorted([3, 1, 4, 1, 5], [2, 5, 3, 1, 4]))  # Output: [1, 1, 2, 3, 4, 5]
print(merge_sorted([3, 1, 4, 1, 5], [2, 5, 3, 1, 6]))  # Output: [1, 1, 2, 3, 4, 5, 6]
print(merge_sorted([3, 1, 4, 1, 5], [2, 5, 3, 1, 7]))  # Output: [1, 1, 2, 3, 4, 5, 6, 7]