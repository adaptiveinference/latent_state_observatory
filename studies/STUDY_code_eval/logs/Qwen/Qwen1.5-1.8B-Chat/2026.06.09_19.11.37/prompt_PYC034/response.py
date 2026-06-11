# CHECK_TOKEN: PYC034

# Define function invert_dict(d) assuming unique values.
def invert_dict(d):
    """
    Invert a dictionary, ensuring that each key-value pair is in reverse order.

    Parameters:
    d (dict): The dictionary to invert.

    Returns:
    dict: The inverted dictionary.
    """
    # Check if the input is a dictionary
    if not isinstance(d, dict):
        raise ValueError("Input must be a dictionary.")

    # Create an empty inverted dictionary
    inverted_dict = {}

    # Iterate over the keys of the original dictionary
    for key, value in d.items():
        # Convert the key to lowercase to handle case-insensitive keys
        key = key.lower()

        # Check if the key is already in the inverted dictionary
        if key in inverted_dict:
            # If it is, invert the value by reversing it
            inverted_dict[key] = value[::-1]
        else:
            # If it is not, add it to the inverted dictionary with the inverted value
            inverted_dict[key] = value

    return inverted_dict

# Test the function
original_dict = {'a': 1, 'b': 2, 'c': 3}
inverted_dict = invert_dict(original_dict)
print(inverted_dict)  # Output: {'c': 3, 'b': 2, 'a': 1}