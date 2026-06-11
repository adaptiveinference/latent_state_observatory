# CHECK_TOKEN: PYC047

# Define function group_by_first_letter(words)
def group_by_first_letter(words):
    # Check if the input is a list of strings
    if not isinstance(words, list):
        raise ValueError("Input must be a list of strings")

    # Initialize an empty dictionary to store the grouped words
    grouped_words = {}

    # Iterate through each word in the list
    for word in words:
        # Split the word into a list of characters
        chars = list(word)

        # Check if the first character is a letter
        if chars[0] in "abcdefghijklmnopqrstuvwxyz":
            # If it is, add the word to the grouped words dictionary with the first character as the key
            if chars[0] in grouped_words:
                grouped_words[chars[0]].append(word)
            else:
                grouped_words[chars[0]] = [word]

    # Return the grouped words dictionary
    return grouped_words

# Test the function
words = ["apple", "banana", "cherry", "date", "elderberry"]
print(group_by_first_letter(words))  # Output: {'apple': ['banana', 'cherry'], 'date': ['elderberry']}

# Explanation:
- The function `group_by_first_letter` takes a list of strings `words` as input.
- First, it checks if the input is a list using the `isinstance` function. If it's not, it raises a `ValueError` with the message "Input must be a list of strings".
- Next, it initializes an empty dictionary `grouped_words` to store the grouped words.
- It iterates through each word in the input list using a `for` loop.
- Inside the loop, it splits each word into a list of characters using the `list` function.
- It checks if the first character of the list is a letter using the `in` operator and the ASCII value of the letter. If it is, it checks if the letter is already a key in the `grouped_words` dictionary. If it is, it appends the word to the corresponding list of words with the first character as the key. If the letter is not already a key, it adds the letter and its corresponding word to the list of words with the first character as the key.
- After iterating through all the words, the function returns the `grouped_words` dictionary, which contains