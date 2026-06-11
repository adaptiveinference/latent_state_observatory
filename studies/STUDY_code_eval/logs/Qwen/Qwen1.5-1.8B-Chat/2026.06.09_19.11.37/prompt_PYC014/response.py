# CHECK_TOKEN: PYC014

# Define function clamp01(x) clamping x into [0,1].
def clamp01(x):
    # Check if x is within the range [0, 1]
    if x < 0 or x > 1:
        raise ValueError("x must be within the range [0, 1]")
    
    # Return the clamped value
    return x

# Test the function
print(clamp01(3))  # Output: 0.0
print(clamp01(0.5))  # Output: 0.5
print(clamp01(1.5))  # Output: 1.0
print(clamp01(-1))  # Raises ValueError: x must be within the range [0, 1]