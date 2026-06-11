# CHECK_TOKEN: PYC056

# Define decorator to count calls
def count_calls(fn):
    # Store wrapper.calls() in a dictionary
    wrapper.calls = {}
    # Check if the function is a function
    if not isinstance(fn, function):
        raise TypeError("Function must be a function")
    # Check if the function is a method
    if not isinstance(fn, method):
        raise TypeError("Function must be a method")
    # Check if the function is a class method
    if not isinstance(fn, classmethod):
        raise TypeError("Function must be a class method")
    # Check if the function is a static method
    if not isinstance(fn, staticmethod):
        raise TypeError("Function must be a static method")
    # Check if the function is a class attribute
    if not isinstance(fn, attribute):
        raise TypeError("Function must be a class attribute")
    # Check if the function is a static attribute
    if not isinstance(fn, attribute):
        raise TypeError("Function must be a static attribute")
    # Check if the function is a class method with the 'def' keyword
    if not isinstance(fn, classmethod) and not fn.__name__ == "__init__":
        raise TypeError("Function must be a class method with the 'def' keyword")
    # Check if the function is a static method with the 'def' keyword
    if not isinstance(fn, classmethod) and not fn.__name__ == "__init__":
        raise TypeError("Function must be a static method with the 'def' keyword")
    # Check if the function is a class method with the 'def' keyword and the 'self' parameter
    if not isinstance(fn, classmethod) and not fn.__name__ == "__init__" and not fn.__self__ == self:
        raise TypeError("Function must be a class method with the 'def' keyword and the 'self' parameter")
    # Check if the function is a static method with the 'def' keyword and the 'self' parameter and the 'self' parameter is a class attribute
    if not isinstance(fn, classmethod) and not fn.__name__ == "__init__" and not fn.__self__ == self and not isinstance(fn.__self__, attribute):
        raise TypeError("Function must be a static method with the 'def' keyword and the 'self' parameter and the 'self' parameter is a class attribute")
   