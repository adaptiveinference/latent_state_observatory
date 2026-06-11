# CHECK_TOKEN: PYC026

# Define function count_vowels(s)
def count_vowels(s):
    """
    This function takes a string as input and returns the number of vowels in the string.

    Args:
        s (str): The input string.

    Returns:
        int: The number of vowels in the string.
    """
    vowels = "aeiouAEIOU"
    count = 0

    for char in s:
        if char in vowels:
            count += 1

    return count

# Test the function
print(count_vowels("Hello, World!"))  # Output: 3
print(count_vowels("Python is a programming language"))  # Output: 4
print(count_vowels("The quick brown fox jumps over the lazy dog"))  # Output: 7
print(count_vowels(""))  # Output: 0
print(count_vowels("Python"))  # Output: 1
print(count_vowels("Python is a programming language"))  # Output: 2
print(count_vowels("Python is a programming language"))  # Output: 3
print(count_vowels("Python is a programming language"))  # Output: 4
print(count_vowels("Python"))  # Output: 5
print(count_vowels("Python is a programming language"))  # Output: 6
print(count_vowels("Python"))  # Output: 7
print(count_vowels("Python"))  # Output: 8
print(count_vowels("Python"))  # Output: 9
print(count_vowels("Python"))  # Output: 10
print(count_vowels("Python"))  # Output: 11
print(count_vowels("Python"))  # Output: 12
print(count_vowels("Python"))  # Output: 13
print(count_vowels("Python"))  # Output: 14
print(count_vowels("Python"))  # Output: 15
print(count_vowels("Python"))  # Output: 16
print(count_vowels("Python"))  # Output: 17
print(count_vowels("Python"))  # Output: 18
print(count_vowels("Python"))  # Output: 19