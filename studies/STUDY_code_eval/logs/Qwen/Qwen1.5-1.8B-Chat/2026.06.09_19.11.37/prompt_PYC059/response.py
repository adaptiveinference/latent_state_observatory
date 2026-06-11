# CHECK_TOKEN: PYC059

# Define function load_json_field
def load_json_field(path, field):
    # Check if the path is a valid JSON file
    if not os.path.exists(path):
        raise ValueError(f"Path '{path}' does not exist.")
    
    # Load the JSON file
    with open(path, 'r') as f:
        # Read the JSON data
        json_data = f.read()
    
    # Check if the specified field exists in the JSON data
    if field not in json_data:
        raise ValueError(f"Field '{field}' not found in the JSON data.")
    
    # Return the loaded JSON field
    return json_data[field]