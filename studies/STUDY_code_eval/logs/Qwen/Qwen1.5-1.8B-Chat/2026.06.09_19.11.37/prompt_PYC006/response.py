# CHECK_TOKEN: PYC006

# Define function get_name(d) returning d['name']..

def get_name(d):
    # Check if the input parameter d is a dictionary
    if not isinstance(d, dict):
        raise ValueError("Input parameter d must be a dictionary.")
    
    # Retrieve the value of the 'name' key from the dictionary
    name = d.get('name')
    
    # Return the name value
    return name

# Test the function
print(get_name({'name': 'John'}))  # Output: John
print(get_name({'name': 'Jane'}))  # Output: Jane
print(get_name({'name': 'World'}))  # Output: World
print(get_name({'name': 'Not a dictionary'}))  # Raises ValueError: Input parameter d must be a dictionary.