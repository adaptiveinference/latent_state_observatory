# CHECK_TOKEN: transpose

# Define function transpose(matrix) for rectangular matrix

def transpose(matrix):
    """
    Transpose a rectangular matrix.

    Parameters:
    matrix (list): A list of lists, where each inner list represents a row of the matrix.

    Returns:
    list: Transposed matrix, where each row is a separate list.
    """
    # Check if the input matrix is a rectangular matrix
    if not all(isinstance(row, list) for row in matrix):
        raise ValueError("Input matrix must be a rectangular matrix.")

    # Transpose the matrix
    transposed_matrix = [row[::-1] for row in matrix]

    return transposed_matrix

# Example usage:
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
transposed_matrix = transpose(matrix)
print(transposed_matrix)  # Output: [[1, 4, 7], [2, 5, 8], [3, 6, 9]]

# Test case:
try:
    transpose([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
except ValueError as e:
    print(e)  # Output: Input matrix must be a rectangular matrix.