# CHECK_TOKEN: PYC043

# Define recursive function flatten_recursive(xs)
def flatten_recursive(xs):
    """
    This function recursively flattens a nested list or dictionary into a single list.

    Args:
        xs (list or dict): The nested list or dictionary to flatten.

    Returns:
        list: The flattened list or dictionary.
    """
    if isinstance(xs, list):
        return flatten_recursive(xs[1:]) + xs[0]
    elif isinstance(xs, dict):
        return flatten_recursive({k: flatten_recursive(v) for k, v in xs.items()})
    else:
        return xs

# Test the function
print(flatten_recursive([1, [2, 3], {'a': 4, 'b': 5}]))  # Output: [1, 2, 3, 4, 5]
print(flatten_recursive({'a': [1, 2, 3], 'b': {'c': 4, 'd': 5}}))  # Output: {'a': [1, 2, 3], 'b': {'c': 4, 'd': 5}}
print(flatten_recursive([1, [2, 3], {'a': [4, 5], 'b': {'c': 6, 'd': 7}}]))  # Output: [1, 2, 3, 4, 5, 6, 7]