# CHECK_TOKEN: knapsack_01

# Function definition for knapsack_01
def knapsack_01(weights, values, capacity):
    # Check if the input parameters are valid
    if not isinstance(weights, list) or not isinstance(values, list) or not isinstance(capacity, int):
        raise ValueError("All input parameters must be lists.")
    
    # Check if the capacity is less than or equal to 0
    if capacity < 0:
        raise ValueError("The capacity must be a non-negative integer.")
    
    # Initialize the maximum value and the current value
    max_value = float('-inf')
    current_value = 0
    
    # Iterate through the weights and values
    for weight in weights:
        for value in values:
            # Calculate the subproblem: find the maximum value that can be obtained by selecting the current weight and value
            sub_value = weight * value + current_value
            # Check if the subproblem is feasible (i.e., the capacity is not exceeded)
            if sub_value <= capacity:
                # Update the maximum value and current value
                max_value = max(max_value, sub_value)
                current_value = sub_value
    
    # Return the maximum value
    return max_value

# Example usage
weights = [10, 20, 30, 40]
values = [60, 80, 100, 120]
capacity = 50

# Call the knapsack_01 function
max_value = knapsack_01(weights, values, capacity)
print("Maximum value:", max_value)  # Output: 150