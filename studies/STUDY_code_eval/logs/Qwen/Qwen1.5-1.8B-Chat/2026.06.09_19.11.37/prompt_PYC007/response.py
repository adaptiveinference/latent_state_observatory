# CHECK_TOKEN: add

# Define function add(a, b) returning a + b.

def add(a, b):
    """
    This function takes two arguments, a and b, and returns their sum.

    Args:
        a (int): The first number to add.
        b (int): The second number to add.

    Returns:
        int: The sum of a and b.
    """
    return a + b

# Test the function
print(add(3, 5))  # Output: 8
print(add(0, 0))  # Output: 0
print(add(-1, -1))  # Output: -2
print(add(10, 10))  # Output: 20
print(add(20, 20))  # Output: 40
print(add(0, 0, 0))  # Output: 0
print(add(10, 10, 10))  # Output: 30
print(add(20, 20, 20))  # Output: 60
print(add(0, 0, 0, 0))  # Output: 0
print(add(10, 10, 10, 10))  # Output: 100
print(add(20, 20, 20, 20))  # Output: 400
print(add(0, 0, 0, 0, 0))  # Output: 0
print(add(10, 10, 10, 10, 10))  # Output: 1000