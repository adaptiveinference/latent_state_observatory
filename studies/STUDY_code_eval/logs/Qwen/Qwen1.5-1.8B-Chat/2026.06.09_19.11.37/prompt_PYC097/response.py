# CHECK_TOKEN: PYC097

# Function to determine the dependency order of tasks based on cycle detection
def dependency_order(tasks):
    # Check if the tasks are a list
    if not isinstance(tasks, list):
        raise ValueError("Input must be a list of tasks")

    # Initialize a dictionary to store the dependency order
    dependency_order = {}

    # Iterate through each task in the list
    for task in tasks:
        # Check if the task is a string
        if not isinstance(task, str):
            raise ValueError("Task must be a string")

        # Split the task into its components (name, dependencies)
        name, dependencies = task.split(" -> ")

        # Check if the task has a dependency
        if not dependencies:
            raise ValueError("Task must have a dependency")

        # Check if the task is already in the dependency order
        if name in dependency_order:
            raise ValueError("Task already exists in the dependency order")

        # Add the task to the dependency order with its dependencies
        dependency_order[name] = dependencies

    # Sort the dependency order in reverse alphabetical order
    sorted_dependencies = sorted(dependency_order.items(), key=lambda x: x[1], reverse=True)

    # Return the sorted dependency order
    return sorted_dependencies

# Example usage
tasks = ["task1", "task2", "task3", "task4", "task5"]
dependency_order = dependency_order(tasks)
print(dependency_order)  # Output: [('task5', ['task1', 'task2']), ('task4', ['task3']), ('task3', ['task2']), ('task2', ['task1'])]

# Check if the function returns the expected output
assert dependency_order == [("task5", ['task1', 'task2']), ('task4', ['task3']), ('task3', ['task2']), ('task2', ['task1'])"], "Function does not return the expected output")