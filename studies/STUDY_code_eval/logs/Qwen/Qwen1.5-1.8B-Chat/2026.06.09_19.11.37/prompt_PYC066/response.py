# CHECK_TOKEN: sliding_window_max_sum

# Function to find the maximum sum of sliding window elements in a given list xs, with a fixed window size k
def sliding_window_max_sum(xs, k):
    """
    This function takes a list xs of integers and a window size k as input, and returns the maximum sum of sliding window elements within the given window.

    Args:
        xs (list): A list of integers representing the elements in the window.
        k (int): The window size.

    Returns:
        int: The maximum sum of sliding window elements within the given window.
    """
    # Initialize variables to store the maximum sum and the current window sum
    max_sum = float('-inf')
    current_sum = 0

    # Iterate over the elements in the window
    for i in range(len(xs) - k + 1):
        # Calculate the current window sum
        current_sum += xs[i]

        # If the current window sum is greater than the maximum sum, update the maximum sum
        if current_sum > max_sum:
            max_sum = current_sum

        # If the current window sum is less than the current window sum, add the element at the current window index to the current sum
        if current_sum < current_sum - k:
            current_sum += xs[i]

    # Return the maximum sum
    return max_sum

# Example usage
xs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
k = 3
max_sum = sliding_window_max_sum(xs, k)
print(f"The maximum sum of sliding window elements within the window of size {k} is {max_sum}.")  # Output: The maximum sum of sliding window elements within the window of size 3 is 21.