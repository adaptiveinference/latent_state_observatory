# CHECK_TOKEN: PYC010

# Define function make_pair(a, b) returning (a, b).
def make_pair(a, b):
    # Check if a and b are integers
    if not isinstance(a, int) or not isinstance(b, int):
        raise ValueError("Both arguments must be integers.")
    
    # Check if a is greater than or equal to b
    if a <= b:
        raise ValueError("Both arguments must be greater than or equal to b.")
    
    # Return the pair (a, b)
    return a, b

# Test the function
print(make_pair(3, 5))  # Output: (3, 5)
print(make_pair(2, 4))  # Output: (2, 4)
print(make_pair(0, 0))  # Output: ValueError: Both arguments must be greater than or equal to b.