# CHECK_TOKEN: PYC086

# Function to retry a function with a maximum number of attempts and a delay in seconds
def retry(fn, attempts, delay_seconds):
    # Check if the function is defined and has the required arguments
    if not fn or not isinstance(fn, (function_type, method_type)):
        raise ValueError("Function must be defined and have the required arguments")

    # Check if the maximum number of attempts is provided
    if attempts < 1:
        raise ValueError("Number of attempts must be greater than 0")

    # Check if the delay in seconds is provided
    if delay_seconds < 0:
        raise ValueError("Delay in seconds must be greater than 0")

    # Create a retry object with the function, attempts, and delay
    retry_obj = Retry(fn, attempts, delay_seconds)

    # Iterate through the attempts and call the function with a delay of 0
    for attempt in range(attempts):
        try:
            return fn()
        except Exception as e:
            # If an exception occurs, add it to the retry object's exceptions list
            retry_obj.exceptions.append(e)

    # If all attempts fail, raise a retry exception with the last exception
    if retry_obj.exceptions:
        raise RetryException(retry_obj.exceptions[-1])

    # Return the result of the function after all attempts
    return retry_obj.result

# Example usage
try:
    # Call the retry function with a maximum of 3 attempts and a delay of 2 seconds
    result = retry(lambda x: x * 2, 3, 2)
    print(result)
except RetryException as e:
    print("Error:", e)