# CHECK_TOKEN: PYC042

# Recursive function to calculate the power of a number x with n as the exponent
def power(x, n):
    # Base case: if n is 0, return 1
    if n == 0:
        return 1
    # Recursive case: calculate the power of x raised to the power of n-1
    else:
        return x * power(x, n-1)

# Example usage
print(power(2, 3))  # Output: 8
print(power(5, 2))  # Output: 25
print(power(10, 1))  # Output: 100
print(power(10, 0))  # Output: 1
print(power(0, 5))  # Output: 0
print(power(0, 0))  # Output: 1

# Explanation:
- The function `power(x, n)` takes two arguments: `x` and `n`.
- The base case checks if `n` is 0. If so, the function returns 1, as 0 to the power of 0 is 1.
- The recursive case calculates the power of `x` raised to the power of `n-1`. It does this by multiplying `x` by the result of calling the `power` function with `x` and `n-1`.
- The function returns the final result of the recursive call.
- The example usage demonstrates the usage of the `power` function with different values of `x` and `n`. The output shows the calculated power of each input number.