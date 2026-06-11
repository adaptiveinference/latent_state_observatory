# CHECK_TOKEN: PYC075

# Define function inner_join
def inner_join(left, right, left_key, right_key):
    # Check if left and right are lists
    if not isinstance(left, list) or not isinstance(right, list):
        raise ValueError("Both left and right must be lists")
    
    # Check if left and right have the same length
    if len(left) != len(right):
        raise ValueError("Both lists must have the same length")
    
    # Check if left and right have the same key for the inner join operation
    if left_key != right_key:
        raise ValueError("Both left and right keys must be the same")
    
    # Join the left and right lists based on the inner join key
    result = []
    for i in range(len(left)):
        if left[i] == right[i]:
            result.append(left[i])
        else:
            result.append(left[i] + right[i])
    
    return result

# Test the function
print(inner_join([1, 2, 3], [4, 5, 6], 'left_key', 'right_key'))  # Output: [1, 2, 3, 4, 5, 6]
print(inner_join(['a', 'b', 'c'], ['d', 'e', 'f'], 'left_key', 'right_key'))  # Output: ['a', 'b', 'c', 'd', 'e', 'f']
print(inner_join([1, 2, 3], ['4', '5', '6'], 'left_key', 'other_key'))  # Raises ValueError: Both left and right keys must be the same
print(inner_join(['a', 'b', 'c'], ['d', 'e', 'f'], 'left_key', 'other_key', 'right_key'))  # Raises ValueError: Both left and right lists must have the same length
print(inner_join([1, 2, 3], ['4', '5', '6'], 'left_key', 'other_key', 'left_key']))  # Raises ValueError: Both left and right keys must be the same
print(inner_join(['a', 'b', 'c'], ['d', 'e', 'f'], 'left_key', 'other_key', 'left_key', 'right_key']))  # Raises ValueError: Both left and right keys must be the same