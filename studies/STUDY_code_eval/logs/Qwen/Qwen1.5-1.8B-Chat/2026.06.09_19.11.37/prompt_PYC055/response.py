# CHECK_TOKEN: PYC055

# Define a generator function chunks(xs, size)
def chunks(xs, size):
    """
    Generator function that generates a sequence of elements from the input list xs, of size size, in chunks of size.

    Args:
        xs (list): The input list of elements.
        size (int): The size of each chunk.

    Returns:
        generator: A generator that yields elements from the input list xs, of size size, in chunks of size.
    """
    for i in range(0, len(xs), size):
        yield xs[i:i+size]  # Yield elements from the start of the list up to the end of the list, but not including the end

# Test the generator function chunks
xs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
size = 3
chunks_result = chunks(xs, size)
for chunk in chunks_result:
    print(chunk)  # Output: [1, 2, 3]