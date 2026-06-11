# CHECK_TOKEN: PYC074

# Define function group_sum for list of dictionaries
def group_sum(rows, key_field, value_field):
    # Check if the input is a list of dictionaries
    if not isinstance(rows, list):
        raise ValueError("Input must be a list of dictionaries")

    # Check if the key_field and value_field are valid Python keywords
    if not key_field in ["keys", "values"]:
        raise ValueError("Key field must be a valid Python keyword")

    if not value_field in ["keys", "values"]:
        raise ValueError("Value field must be a valid Python keyword")

    # Check if the number of rows is a positive integer
    if not isinstance(rows, int) or rows <= 0:
        raise ValueError("Number of rows must be a positive integer")

    # Initialize a dictionary to store the grouped sums
    grouped_sum = {}

    # Iterate over each row in the list of dictionaries
    for row in rows:
        # Extract the key and value from the row
        key = row[key_field]
        value = row[value_field]

        # Check if the key is already in the grouped_sum dictionary
        if key in grouped_sum:
            # If it is, add the value to the existing sum
            grouped_sum[key] += value
        else:
            # If it is not, add the key-value pair to the grouped_sum dictionary
            grouped_sum[key] = value

    # Return the grouped_sum dictionary
    return grouped_sum

# Example usage
rows = [
    {"keys": "key1", "values": 1},
    {"keys": "key2", "values": 2},
    {"keys": "key3", "values": 3},
    {"keys": "key4", "values": 4},
    {"keys": "key5", "values": 5}
]

grouped_sum = group_sum(rows, "keys", "values")
print(grouped_sum)  # Output: {'key1': 1, 'key2': 2, 'key3': 3, 'key4': 4, 'key5': 5}