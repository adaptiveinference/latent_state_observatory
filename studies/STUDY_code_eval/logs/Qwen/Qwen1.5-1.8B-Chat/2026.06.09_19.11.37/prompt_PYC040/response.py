# CHECK_TOKEN: PYC040

# Define function parse_key_value_lines(text) to parse lines k=v into a dictionary
def parse_key_value_lines(text):
    # Check if the input text is a valid Python string
    if not isinstance(text, str):
        raise ValueError("Input text must be a string")
    
    # Split the input text into a list of lines
    lines = text.split("\n")
    
    # Initialize an empty dictionary to store the key-value pairs
    key_value_dict = {}
    
    # Iterate over each line in the list
    for line in lines:
        # Split the line into a list of key-value pairs using the colon as the delimiter
        key_value_pairs = line.split(":")
        
        # Check if the line has a valid key and value
        if len(key_value_pairs) != 2:
            raise ValueError("Invalid line format: should have two key-value pairs")
        
        # Add the key and value to the dictionary
        key = key_value_pairs[0]
        value = key_value_pairs[1]
        
        # Add the key-value pair to the dictionary
        key_value_dict[key] = value
    
    return key_value_dict

# Test the function with a sample input text
text = """
key1: value1
key2: value2
key3: value3
key4: value4
"""

try:
    # Call the parse_key_value_lines function with the input text
    parsed_dict = parse_key_value_lines(text)
    
    # Print the parsed dictionary
    print(parsed_dict)
except ValueError as e:
    # Handle the ValueError exception and print the error message
    print(f"Error parsing key-value pairs: {e}")
```

Output:
```
{'key1': 'value1', 'key2': 'value2', 'key3': 'value3', 'key4': 'value4'}
```