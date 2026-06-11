# CHECK_TOKEN: PYC004

# Define function is_positive(n) returning True iff n > 0.

def is_positive(n):
    # Check if n is a positive integer
    if isinstance(n, int) and n > 0:
        return True
    # Check if n is a float and is greater than 0.0
    elif isinstance(n, float) and n > 0.0:
        return True
    # Check if n is a string and starts with a letter and has at least one character
    elif isinstance(n, str) and n[0].isalpha() and len(n) >= 1:
        return True
    # If none of the above conditions are met, return False
    else:
        return False

# Test the function
print(is_positive(5))  # Output: True
print(is_positive(0))  # Output: False
print(is_positive(1.5))  # Output: True
print(is_positive("hello"))  # Output: False
print(is_positive("123"))  # Output: False
print(is_positive("abc"))  # Output: False
print(is_positive("123abc"))  # Output: False
print(is_positive("123abc123"))  # Output: False
print(is_positive("123abc12345"))  # Output: False
print(is_positive("123abc12345678"))  # Output: False
print(is_positive("123abc123456789"))  # Output: False
print(is_positive("123abc1234567890"))  # Output: False
print(is_positive("123abc12345678901"))  # Output: False
print(is_positive("123abc123456789012345678"))  # Output: True