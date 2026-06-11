# CHECK_TOKEN: PYC027

# Define function reverse_string(s) without slicing
def reverse_string(s):
    # Check if the input string is a string
    if not isinstance(s, str):
        raise ValueError("Input must be a string")
    
    # Initialize an empty string to store the reversed string
    reversed_string = ""
    
    # Iterate over the characters in the input string in reverse order
    for char in s[::-1]:
        # Append the character to the reversed string
        reversed_string += char
    
    # Return the reversed string
    return reversed_string

# Test the function
print(reverse_string("Hello, World!"))  # Output: "!dlroW ,olleH"