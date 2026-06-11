# CHECK_TOKEN: PYC045

# Definition for insertion sort
def insertion_sort(xs):
    """
    Sort a list of integers using insertion sort.

    :type xs: List[int]
    :rtype: List[int]
    """
    # Initialize an empty list to store the sorted elements
    sorted_list = []

    # Iterate over the input list
    for i in range(1, len(xs)):
        # Find the current element and its index in the sorted list
        current_index = i
        while current_index > 0 and xs[current_index] < xs[current_index - 1]:
            # Shift the elements to the right until the correct position is found
            xs[current_index], xs[current_index - 1] = xs[current_index - 1], xs[current_index]
            current_index -= 1

    # Return the sorted list
    return xs

# Test the insertion_sort function
print(insertion_sort([3, 1, 4, 1, 5, 9, 2, 6, 5, 3]))  # Output: [1, 1, 2, 3, 3, 4, 5, 5, 6, 9]