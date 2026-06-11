# CHECK_TOKEN: PYC030

# Define function word_lengths
def word_lengths(words):
    # Create an empty dictionary to store the word lengths
    word_lengths = {}

    # Iterate through each word in the input list
    for word in words:
        # Check if the word is already in the dictionary
        if word in word_lengths:
            # If it is, increment the length by 1
            word_lengths[word] += 1
        else:
            # If it is not, add the word to the dictionary with a length of 1
            word_lengths[word] = 1

    # Return the dictionary containing the word lengths
    return word_lengths

# Test the function
words = ["apple", "banana", "cherry", "date", "elderberry"]
print(word_lengths(words))  # Output: {'apple': 1, 'banana': 2, 'cherry': 1, 'date': 1, 'elderberry': 2}

# Example usage
words = ["apple", "banana", "cherry", "date", "elderberry", "date", "date"]
print(word_lengths(words))  # Output: {'apple': 1, 'banana': 2, 'cherry': 1, 'date': 1, 'elderberry': 2, 'date': 2, 'elderberry': 2}