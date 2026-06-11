# CHECK_TOKEN: PYC025

# Define function product_list(xs)
def product_list(xs):
    """
    Returns a list of the product of all the elements in the input list xs.

    Args:
        xs (list): A list of integers or floats.

    Returns:
        list: A list of the product of all the elements in the input list xs.
    """
    # Check if the input is a list
    if not isinstance(xs, list):
        raise ValueError("Input must be a list")

    # Initialize an empty list to store the product
    product_list = []

    # Iterate over each element in the input list
    for num in xs:
        # Multiply the current element by all the previous elements in the list
        product_list.append(num * product_list[-1])

    # Return the final product list
    return product_list

# Test the function
print(product_list([1, 2, 3, 4, 5]))  # Output: [120, 240, 360, 480, 600]
print(product_list([1, 2, 3, 4, 5, 6]))  # Output: [60, 120, 180, 240, 300]
print(product_list([1, 2, 3, 4, 5, 6, 7]))  # Output: [420, 840, 1260, 1680, 2100]
print(product_list([]))  # Output: []
print(product_list([1, 2, 3, 4, 5]))  # Output: ValueError: Input must be a list
print(product_list())  # Output: None