# CHECK_TOKEN: PYC018

# Define function get_or_zero(d, key) returning d[key] or 0.

def get_or_zero(d, key):
    # Check if the key exists in the dictionary d
    if key in d:
        # Return the value associated with the key
        return d[key]
    # If the key is not found, return 0
    else:
        # Return 0 to indicate that the key was not found
        return 0

# Test the function with a sample dictionary
my_dict = {'a': 1, 'b': 2, 'c': 3}
print(get_or_zero(my_dict, 'b'))  # Output: 2
print(get_or_zero(my_dict, 'd'))  # Output: 0
print(get_or_zero(my_dict, 'e'))  # Output: 0
print(get_or_zero(my_dict, 'f'))  # Output: 0
print(get_or_zero(my_dict, 'g'))  # Output: 0
print(get_or_zero(my_dict, 'h'))  # Output: 0
print(get_or_zero(my_dict, 'i'))  # Output: 0
print(get_or_zero(my_dict, 'j'))  # Output: 0
print(get_or_zero(my_dict, 'k'))  # Output: 0
print(get_or_zero(my_dict, 'l'))  # Output: 0
print(get_or_zero(my_dict, 'm'))  # Output: 0
print(get_or_zero(my_dict, 'n'))  # Output: 0
print(get_or_zero(my_dict, 'o'))  # Output: 0
print(get_or_zero(my_dict, 'p'))  # Output: 0
print(get_or_zero(my_dict, 'q'))  # Output: 0
print(get_or_zero(my_dict, 'r'))  # Output: 0
print(get_or_zero(my_dict, 's'))  # Output: 0
print(get_or_zero(my_dict, 't'))  # Output: 0
print(get_or_zero(my_dict, 'u'))  # Output: 0
print(get_or_zero(my_dict, 'v'))  # Output: 0
print(get_or_zero(my_dict, 'w'))  # Output: 0
print(get_or_zero(my_dict, 'x