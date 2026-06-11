# CHECK_TOKEN: PYC011

# Define function even_or_odd(n) returning 'even' or 'odd'.
def even_or_odd(n):
    # Check if the input number is positive
    if n > 0:
        # Check if the number is even
        if n % 2 == 0:
            return 'even'
        # Check if the number is odd
        else:
            return 'odd'
    # If the input number is negative, return 'odd'
    else:
        return 'odd'