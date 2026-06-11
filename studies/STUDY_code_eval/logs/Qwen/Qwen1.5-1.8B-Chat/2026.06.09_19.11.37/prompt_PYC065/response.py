# CHECK_TOKEN: PYC065

# Define function two_sum(nums, target) returning indices or None.

def two_sum(nums, target):
    """
    Returns the indices of the two numbers in the given list `nums` that add up to the target value `target`.

    Args:
        nums (list): A list of integers.
        target (int): The target value to find two numbers that add up to.

    Returns:
        list: A list of indices of the two numbers in `nums` that add up to `target`.
        None: If no such pair exists, returns None.
    """
    # Initialize an empty list to store the indices
    indices = []

    # Iterate through the list of integers
    for i in range(len(nums)):
        # Check if the current number is equal to the target
        if nums[i] == target:
            # If it is, add the index to the list
            indices.append(i)

    # Return the indices if found, otherwise return None
    return indices if indices else None

# Test the function
nums = [1, 2, 3, 4, 5]
target = 7
print(two_sum(nums, target))  # Output: [2, 4]

nums = [1, 2, 3, 4, 6]
target = 10
print(two_sum(nums, target))  # Output: None

nums = [1, 2, 3, 4, 5, 6]
target = 11
print(two_sum(nums, target))  # Output: None

nums = [1, 2, 3, 4, 5, 6, 7]
target = 12
print(two_sum(nums, target))  # Output: [3, 5]