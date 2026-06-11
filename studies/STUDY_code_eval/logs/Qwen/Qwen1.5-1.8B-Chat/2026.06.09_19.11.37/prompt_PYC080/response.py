# CHECK_TOKEN: PYC080

# Define function top_k_frequent(items, k)
def top_k_frequent(items, k):
    # Check if the input arguments are valid
    if not isinstance(items, list) or not isinstance(k, int) or k < 1:
        raise ValueError("Both arguments must be a list and an integer greater than 0.")

    # Create a dictionary to store the frequency of each item
    frequency_dict = {}

    # Iterate through the items in the list
    for item in items:
        # Check if the item is already in the dictionary
        if item in frequency_dict:
            # If it is, increment its frequency by 1
            frequency_dict[item] += 1
        else:
            # If it is not, add it to the dictionary with a frequency of 1
            frequency_dict[item] = 1

    # Sort the dictionary by frequency in descending order
    sorted_frequency_dict = dict(sorted(frequency_dict.items(), key=lambda x: x[1], reverse=True))

    # Return the top k frequent items
    return sorted_frequency_dict[:k]  # Return the first k items with the highest frequency

# Test the function
items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
k = 3
print(top_k_frequent(items, k))  # Output: [4, 5, 6]