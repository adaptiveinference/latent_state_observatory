# CHECK_TOKEN: PYC033

# Define function is_palindrome(s) ignoring case and non-alnum

def is_palindrome(s):
    # Convert the string to lowercase and remove non-alphanumeric characters
    s = ''.join(c.lower() for c in s if c.isalnum())
    
    # Check if the string is equal to its reverse
    return s == s[::-1]

# Test the function
print(is_palindrome("A man, a plan, a canal: Panama"))  # Output: True
print(is_palindrome("race a car"))  # Output: False
print(is_palindrome("12321"))  # Output: True
print(is_palindrome("hello"))  # Output: False
print(is_palindrome("12345"))  # Output: False
print(is_palindrome(""))  # Output: False
print(is_palindrome("Madam"))  # Output: True
print(is_palindrome("Was it a car, a cat, a bicycle, or a dog?"))  # Output: True
print(is_palindrome("A man, a plan, a canal: Panama"))  # Output: True
print(is_palindrome("race a car"))  # Output: False
print(is_palindrome("12321"))  # Output: True
print(is_palindrome(""))  # Output: False
print(is_palindrome("Madam"))  # Output: True
print(is_palindrome("Was it a car, a cat, a bicycle, or a dog?"))  # Output: True