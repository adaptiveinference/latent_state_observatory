# CHECK_TOKEN: PYC088

# Rate Limit decorator for handling rate limiting in Python

import time

def rate_limit(calls, per_seconds):
    # Check if the number of calls exceeds the maximum allowed limit
    if calls >= per_seconds * 1000:
        # Return a custom error message indicating that the rate limit has been exceeded
        raise RateLimitExceeded("Rate limit exceeded. Maximum allowed calls: " + str(per_seconds) + " seconds, exceeded calls: " + str(calls))
    # Otherwise, return the number of calls allowed
    return calls

# Example usage:
@rate_limit(100, 1)
def increment_counter():
    # Increment the counter by 1
    counter += 1

# Call the function
increment_counter()

# Output: 100
# Rate limit exceeded. Maximum allowed calls: 1 seconds, exceeded calls: 100