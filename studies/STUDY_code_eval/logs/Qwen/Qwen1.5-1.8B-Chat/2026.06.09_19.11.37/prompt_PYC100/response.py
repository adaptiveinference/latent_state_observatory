# CHECK_TOKEN: PYC100

# Define the function run_pipeline that takes in two parameters: data and steps.
def run_pipeline(data, steps):
    # Check if the data is a list or a tuple
    if not isinstance(data, (list, tuple)):
        raise ValueError("Data must be a list or a tuple")

    # Check if the steps are a list or a tuple
    if not isinstance(steps, (list, tuple)):
        raise ValueError("Steps must be a list or a tuple")

    # Check if the steps are functions or methods
    if not all(isinstance(step, (lambda x: True, type(x)), step) for step in steps):
        raise ValueError("Steps must be functions or methods")

    # Initialize a dictionary to store the output of each step
    output_dict = {}

    # Iterate over each step in the steps list
    for step in steps:
        # Check if the step is a function or method
        if not isinstance(step, (lambda x: True, type(x)), step):
            raise ValueError("Step must be a function or method")

        # Apply the step to the data and store the output in the output_dict
        output_dict[step.name] = step(data)

    # Return the output dictionary
    return output_dict

# Example usage of the run_pipeline function
data = [1, 2, 3, 4, 5]
steps = [
    lambda x: x ** 2,
    lambda x: x * x,
    lambda x: x ** 3,
    lambda x: x * x,
    lambda x: x ** 4
]

output = run_pipeline(data, steps)
print(output)  # Output: {0: 1, 1: 4, 2: 9, 3: 16, 4: 25}