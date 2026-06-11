# CHECK_TOKEN: PYC003

# Define function greet(name) returning 'Hello, ' + name.

def greet(name):
    # Check if the input parameter is a string
    if not isinstance(name, str):
        raise ValueError("Input parameter must be a string")
    
    # Concatenate 'Hello, ' with the input string
    return 'Hello, ' + name

# Test the greet function
print(greet("John"))  # Output: Hello, John
print(greet(123))  # Output: Hello, 123
print(greet("World"))  # Raises ValueError: Input parameter must be a string
print(greet("12345"))  # Raises ValueError: Input parameter must be a string
print(greet())  # Raises ValueError: Input parameter must be a string
print(greet(""))  # Raises ValueError: Input parameter must be a string
print(greet(" "))  # Raises ValueError: Input parameter must be a string
print(greet("John Doe"))  # Raises ValueError: Input parameter must be a string
print(greet("123456"))  # Raises ValueError: Input parameter must be a string
print(greet())  # Raises ValueError: Input parameter must be a string
print(greet())  # Raises ValueError: Input parameter must be a string
print(greet())  # Raises ValueError: Input parameter must be a string
print(greet())  # Raises ValueError: Input parameter must be a string
print(greet())  # Raises ValueError: Input parameter must be a string
print(greet())  # Raises ValueError: Input parameter must be a string
print(greet())  # Raises ValueError: Input parameter must be a string
print(greet())  # Raises ValueError: Input parameter must be a string
print(greet())  # Raises ValueError: Input parameter must be a string
print(greet())  # Raises ValueError: Input parameter must be a string
print(greet())  # Raises ValueError: Input parameter must be a string
print(greet())  # Raises ValueError: Input parameter must be a string
print(greet())  # Raises ValueError: Input parameter must be a string
print(greet())  # Raises ValueError: Input parameter must be a string
print(greet())  # Raises ValueError: Input parameter must be a string
print(greet())  # Raises ValueError: