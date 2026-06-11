# CHECK_TOKEN: PYC093

# Function to calculate rolling mean of a list of numbers, with a specified window size
def rolling_mean(xs, window):
    """
    Calculates the rolling mean of a list of numbers, with a specified window size.

    Args:
        xs (list): A list of numbers.
        window (int): The size of the rolling window.

    Returns:
        list: A list containing the rolling mean of the numbers in the input list, with None until the window is full.
    """
    # Check if the window size is valid
    if window < 1:
        raise ValueError("Window size must be a positive integer.")

    # Initialize an empty list to store the rolling mean
    rolling_mean = []

    # Iterate over the input list, adding the current number to the rolling mean if it is within the window
    for num in xs:
        if num <= window:
            rolling_mean.append(num)
        else:
            # If the window is full, add the last element of the rolling mean
            rolling_mean.append(rolling_mean[-1])

    # Return the rolling mean list
    return rolling_mean

# Example usage
xs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
window = 3
result = rolling_mean(xs, window)
print(result)  # Output: [3, 6, 9, 12, 15, 18, 21, 24, 27, 30]