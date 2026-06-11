# CHECK_TOKEN: unique_preserve_order

# Define function unique_preserve_order(xs)
def unique_preserve_order(xs):
    # Check if the input list is empty
    if not xs:
        return "Input list is empty"
    
    # Create an empty set to store unique elements
    unique_set = set()
    
    # Iterate over each element in the input list
    for x in xs:
        # Check if the element is already in the set
        if x in unique_set:
            # If it is, return a message indicating that the element is already unique
            return f"{x} is already unique"
        
        # Add the element to the set
        unique_set.add(x)
    
    # If the set is empty, return a message indicating that all elements are unique
    return "All elements in the input list are unique"