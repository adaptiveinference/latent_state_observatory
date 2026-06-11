# CHECK_TOKEN: PYC008

# Define function shout(s) returning s.upper()
def shout(s):
    # Check if the input string s is a valid Python string
    if not isinstance(s, str):
        raise ValueError("Input must be a string")
    
    # Convert the string to uppercase using the upper() method
    return s.upper()

# Test the function
print(shout("hello"))  # Output: "HELLO"
print(shout("123"))  # Output: "123"
print(shout(""))  # Output: ""
print(shout("abc"))  # Raises ValueError: Input must be a string
print(shout(123))  # Raises ValueError: Input must be a string
print(shout("Python"))  # Raises ValueError: Input must be a string
print(shout("12345"))  # Raises ValueError: Input must be a string
print(shout("Python"))  # Output: "PYTHON"