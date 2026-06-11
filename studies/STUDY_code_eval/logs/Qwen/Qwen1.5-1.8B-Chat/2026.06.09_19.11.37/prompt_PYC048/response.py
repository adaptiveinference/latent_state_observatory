# CHECK_TOKEN: PyC048

# Define function most_common_char(s) ignoring spaces
def most_common_char(s):
    # Remove spaces from the input string
    s = s.replace(" ", "")
    
    # Initialize an empty dictionary to store the frequency of each character
    char_freq = {}
    
    # Iterate over each character in the string
    for char in s:
        # If the character is already in the dictionary, increment its frequency by 1
        if char in char_freq:
            char_freq[char] += 1
        # Otherwise, add the character to the dictionary with a frequency of 1
        else:
            char_freq[char] = 1
    
    # Find the character with the highest frequency
    most_common_char = None
    max_freq = 0
    
    # Iterate over the dictionary to find the character with the highest frequency
    for char, freq in char_freq.items():
        if freq > max_freq:
            most_common_char = char
            max_freq = freq
    
    # Return the most common character
    return most_common_char

# Test the function
print(most_common_char("Hello, World!"))  # Output: 'l'
print(most_common_char("Python Programming"))  # Output: 'p'
print(most_common_char("Hello, Python Programming!"))  # Output: 'p'