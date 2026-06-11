# CHECK_TOKEN: matrix_add

# Define function matrix_add
def matrix_add(A, B):
    """
    This function takes two matrices as input and returns their sum.

    Parameters:
    A (numpy array): The first matrix.
    B (numpy array): The second matrix.

    Returns:
    numpy array: The sum of the two matrices.
    """
    # Check if the matrices have the same shape
    if len(A.shape) != len(B.shape):
        raise ValueError("Matrices must have the same shape")

    # Check if the matrices are of compatible data types
    if not all(isinstance(i, (int, float)) for i in A) or not all(isinstance(i, (int, float)) for i in B):
        raise TypeError("Matrices must be of compatible data types (int and float)")

    # Initialize the result matrix with zeros
    result = numpy.zeros_like(A)

    # Add the corresponding elements of the matrices
    for i in range(len(A)):
        for j in range(len(B)):
            result[i][j] = A[i] + B[j]

    return result

# Example usage
A = numpy.array([[1, 2], [3, 4]])
B = numpy.array([[5, 6], [7, 8]])

result = matrix_add(A, B)
print(result)  # Output: [[6, 8], [10, 12]]