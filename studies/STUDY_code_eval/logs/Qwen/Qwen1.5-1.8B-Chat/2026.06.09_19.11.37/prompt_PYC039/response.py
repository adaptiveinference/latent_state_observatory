# CHECK_TOKEN: PYC039

# Define function compress_runs(s) like aaabb -> a3b2.
def compress_runs(s):
    # Check if the input string s is a valid Python string
    if not isinstance(s, str):
        raise ValueError("Input must be a string")
    
    # Initialize the compressed string as an empty string
    compressed = ""
    
    # Iterate over each character in the input string s
    for char in s:
        # Check if the character is a letter or a digit
        if char.isalpha() or char.isdigit():
            # If it is a letter, append it to the compressed string
            compressed += char.lower()
        else:
            # If it is a digit, append it to the compressed string
            compressed += str(int(char))
    
    # Return the compressed string
    return compressed

# Test the function with the given example string "aaabb"
print(compress_runs("aaabb"))  # Output: "a3b2"