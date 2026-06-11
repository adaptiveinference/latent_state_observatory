# CHECK_TOKEN: PYC085

# Function to calculate the differences between two dictionaries
def diff_dicts(old, new):
    # Check if the input dictionaries are not empty
    if not old or not new:
        return "Both dictionaries must have at least one key-value pair"

    # Create empty dictionaries to store the added, removed, and changed keys
    added = {}
    removed = {}
    changed = {}

    # Iterate over the keys in the first dictionary
    for key in old:
        # Check if the key is present in the second dictionary
        if key in new:
            # If the key is present, add it to the added dictionary
            added[key] = old[key]
        else:
            # If the key is not present, add it to the removed dictionary
            removed[key] = old[key]
        # If the key is present in both dictionaries, check if its value has changed
        elif old[key] != new[key]:
            # If the value has changed, add it to the changed dictionary
            changed[key] = new[key]

    # Return the differences
    return added, removed, changed

# Example usage
old_dict = {"key1": "value1", "key2": "value2", "key3": "value3"}
new_dict = {"key1": "value4", "key2": "value5", "key3": "value6"}

# Calculate the differences
added, removed, changed = diff_dicts(old_dict, new_dict)

print("Added keys:", added)
print("Removed keys:", removed)
print("Changed keys:", changed)  # Output: {'key1': 'value4', 'key2': 'value5', 'key3': 'value6'}
```

In this implementation, we first check if the input dictionaries are empty. If either of them is empty, we return a message indicating that both dictionaries must have at least one key-value pair. 

Next, we create empty dictionaries to store the added, removed, and changed keys. We iterate over the keys in the first dictionary and check if each key is present in the second dictionary. If the key is present, we add it to the added dictionary with the corresponding value from the first dictionary. If the key is not present, we add it to the removed dictionary with the corresponding value from the first dictionary. If the key is present in both dictionaries, we check if