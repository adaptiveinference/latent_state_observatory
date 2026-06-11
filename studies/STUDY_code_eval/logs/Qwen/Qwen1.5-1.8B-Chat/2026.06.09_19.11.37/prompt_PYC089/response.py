# CHECK_TOKEN: reconcile_inventory

# Function to reconcile inventory
def reconcile_inventory(expected, observed):
    """
    This function takes in two lists, `expected` and `observed`, representing the inventory of a store. It returns a new list that contains the items in `expected` that are not present in `observed`.

    Args:
        expected (list): A list of items expected to be in the inventory.
        observed (list): A list of items observed in the inventory.

    Returns:
        list: A list of items in `expected` that are not present in `observed`.
    """
    # Check if the lengths of the lists are equal
    if len(expected) != len(observed):
        raise ValueError("The lengths of the expected and observed lists must be equal.")

    # Create a new list to store the non-present items
    non_present_items = []

    # Iterate over the expected items
    for item in expected:
        # Check if the item is not present in the observed items
        if item not in observed:
            non_present_items.append(item)

    # Return the non-present items
    return non_present_items

# Example usage
expected = [1, 2, 3, 4, 5]
observed = [1, 2, 3, 6, 7]

non_present_items = reconcile_inventory(expected, observed)
print(non_present_items)  # Output: [4, 5, 6, 7]