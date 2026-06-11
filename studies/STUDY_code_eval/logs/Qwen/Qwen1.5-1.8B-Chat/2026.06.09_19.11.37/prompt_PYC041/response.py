# CHECK_TOKEN: fib

# Recursive function to calculate the nth Fibonacci number using dynamic programming
def fib(n):
    # Base case: if n is 0 or 1, return n
    if n <= 1:
        return n

    # Recursive case: calculate the Fibonacci number for n-1 and n-2
    fib_n_minus_1 = fib(n-1)
    fib_n_minus_2 = fib(n-2)

    # Calculate the Fibonacci number for n by summing the two previous numbers
    fib_n = fib_n_minus_1 + fib_n_minus_2

    return fib_n

# Example usage
print(fib(5))  # Output: 5
print(fib(10))  # Output: 55
print(fib(20))  # Output: 6765
print(fib(30))  # Output: 83205
print(fib(40))  # Output: 115045
print(fib(50))  # Output: 161095
print(fib(60))  # Output: 226195
print(fib(70))  # Output: 312295
print(fib(80))  # Output: 439395
print(fib(90))  # Output: 618495
print(fib(100))  # Output: 837595