# CHECK_TOKEN: PYC058

# Define function read_nonempty_lines
def read_nonempty_lines(path):
    # Check if the path is a valid file path
    if not os.path.exists(path):
        raise ValueError(f"Path '{path}' does not exist.")
    
    # Read the file content
    with open(path, 'r') as file:
        content = file.read()
    
    # Check if the file content is empty
    if not content:
        return "File is empty."
    
    # Return the file content
    return content

# Example usage
path = "/path/to/your/file.txt"
nonempty_lines = read_nonempty_lines(path)
print(nonempty_lines)  # Output: File is empty.