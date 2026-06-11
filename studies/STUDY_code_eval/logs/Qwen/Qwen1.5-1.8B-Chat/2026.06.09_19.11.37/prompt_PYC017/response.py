# CHECK_TOKEN: safe_first

# Define function safe_first(xs, default=None)
def safe_first(xs: List[int], default=None):
    # Check if the list is empty
    if not xs:
        return default

    # Check if the first element of the list is a positive integer
    if not isinstance(xs[0], int) or xs[0] <= 0:
        return default

    # Check if the first element is greater than or equal to the second element
    if xs[0] >= xs[1]:
        return default

    # If all conditions are met, return the first element
    return xs[0]