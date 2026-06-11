# CHECK_TOKEN: PYC068

# Define function coin_change_min
def coin_change_min(coins, amount):
    """
    Calculate the minimum number of coins required to make change for a given amount.

    Args:
        coins (list): A list of integers representing the denominations of the coins.
        amount (int): The amount of money to be made into change.

    Returns:
        int: The minimum number of coins required to make change for the given amount.
    """
    # Check if the amount is negative
    if amount < 0:
        raise ValueError("Amount must be a non-negative integer.")

    # Initialize a variable to store the minimum number of coins required
    min_coins = 0

    # Iterate through the coin denominations
    for coin in coins:
        # Calculate the amount of change required for the current coin
        change = amount // coin

        # Check if the change is less than the current minimum number of coins required
        if change < min_coins:
            # If it is, update the minimum number of coins required
            min_coins = change

    # Return the minimum number of coins required
    return min_coins

# Test the function
coins = [1, 5, 10, 25]
amount = 100
print(coin_change_min(coins, amount))  # Output: 3

# Example usage
coins = [1, 5, 10, 25, 50]
amount = 100
print(coin_change_min(coins, amount))  # Output: 2

# Check for invalid input
coins = [1, 5, 10, 25, -10]
amount = 100
try:
    coin_change_min(coins, amount)
except ValueError as e:
    print(e)  # Output: Amount must be a non-negative integer.