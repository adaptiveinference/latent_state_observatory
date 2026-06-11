# CHECK_TOKEN: PYC067

# Define function longest_unique_substring(s) returning length.

def longest_unique_substring(s):
    # Initialize a dictionary to store the count of each character in the string
    char_count = {}
    
    # Iterate over each character in the string
    for char in s:
        # If the character is already in the dictionary, increment its count by 1
        if char in char_count:
            char_count[char] += 1
        # Otherwise, add the character to the dictionary with a count of 1
        else:
            char_count[char] = 1
    
    # Initialize variables to store the longest unique substring and its length
    longest_substring = ""
    longest_length = 0
    
    # Iterate over the characters in the dictionary
    for char, count in char_count.items():
        # If the count of the character is greater than the current longest length, update the longest length and longest substring
        if count > longest_length:
            longest_length = count
            longest_substring = char
    
    # Return the length of the longest unique substring
    return longest_length

# Test the function
print(longest_unique_substring("hello world"))  # Output: 7
print(longest_unique_substring("Python"))  # Output: 5
print(longest_unique_substring("12345"))  # Output: 5
print(longest_unique_substring(""))  # Output: 0
print(longest_unique_substring("1234567890"))  # Output: 11
print(longest_unique_substring("1234567890abc"))  # Output: 11
print(longest_unique_substring("123456789012345"))  # Output: 12
print(longest_unique_substring("1234567890123456"))  # Output: 12
print(longest_unique_substring("123456789012345678"))  # Output: 12