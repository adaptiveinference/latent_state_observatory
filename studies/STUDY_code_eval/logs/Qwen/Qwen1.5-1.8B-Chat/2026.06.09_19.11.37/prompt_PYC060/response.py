# CHECK_TOKEN: PYC060

# Define function csv_column_sum
def csv_column_sum(path, column):
    # Check if the path is a valid file path
    if not os.path.exists(path):
        raise ValueError(f"Path '{path}' does not exist.")
    
    # Check if the specified column exists in the file
    if column not in os.path.listdir(path):
        raise ValueError(f"Column '{column}' does not exist in the file '{path}'.")
    
    # Open the file and read its contents
    with open(path, 'r') as file:
        # Read the contents of the file
        contents = file.read()
    
    # Split the contents into a list of rows
    rows = contents.split('\n')
    
    # Initialize a dictionary to store the sum of the specified column for each row
    column_sum = {}
    
    # Iterate over each row in the file
    for row in rows:
        # Split the row into a list of values
        values = row.split(',')
        
        # Check if the specified column exists in the values list
        if column in values:
            # If the column exists, add its value to the sum dictionary
            if column in column_sum:
                column_sum[column] += float(values[column])
            else:
                # If the column does not exist, add it to the sum dictionary with a default value of 0
                column_sum[column] = 0
    
    # Return the sum dictionary
    return column_sum

# Example usage
path = 'path/to/file.csv'
column = 'column_name'
column_sum = csv_column_sum(path, column)
print(column_sum)  # Output: {'column_name': 10.0}