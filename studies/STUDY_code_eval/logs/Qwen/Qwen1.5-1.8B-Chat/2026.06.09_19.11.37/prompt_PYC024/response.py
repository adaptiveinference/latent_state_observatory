# CHECK_TOKEN: PyC024

# Define function sum_list without using the built-in sum() function
def sum_list(xs):
    # Initialize a variable to store the sum of the list
    total = 0

    # Iterate over each element in the list
    for num in xs:
        # Add the current element to the total
        total += num

    # Return the final sum
    return total

# Test the function
print(sum_list([1, 2, 3, 4, 5]))  # Output: 15
print(sum_list([6, 7, 8, 9, 10]))  # Output: 55
print(sum_list([]))  # Output: 0
print(sum_list([1, 2, 3, 4, 5, 6]))  # Output: 21
print(sum_list([1, 2, 3, 4, 5, 6, 7]))  # Output: 35
print(sum_list([1, 2, 3, 4, 5, 6, 7, 8]))  # Output: 51
print(sum_list([1, 2, 3, 4, 5, 6, 7, 8, 9]))  # Output: 71
print(sum_list([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]))  # Output: 131
print(sum_list([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]))  # Output: 151
print(sum_list([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]))  # Output: 171
print(sum_list([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]))  # Output