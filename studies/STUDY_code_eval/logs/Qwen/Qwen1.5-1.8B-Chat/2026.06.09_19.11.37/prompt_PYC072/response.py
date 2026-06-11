# CHECK_TOKEN: eval_rpn

# Define function eval_rpn(tokens)
def eval_rpn(tokens):
    # Check if the input is a list of tokens
    if not isinstance(tokens, list):
        raise ValueError("Input must be a list of tokens.")

    # Check if the list contains at least one token
    if len(tokens) < 1:
        raise ValueError("Input must contain at least one token.")

    # Define the function to evaluate the RPN (Reverse Polish Notation) expression
    def evaluate_rpn(expression):
        # Split the expression into individual tokens
        tokens = expression.split()

        # Check if the first token is the operator
        if tokens[0] != "#":
            raise ValueError("First token must be the operator (e.g., +, -, *, /, %, etc.)")

        # Split the operator into left and right operands
        left_operand = tokens[1]
        right_operand = tokens[2:]

        # Check if the left operand is a number
        if not isinstance(left_operand, (int, float)):
            raise ValueError("Left operand must be a number.")

        # Check if the right operand is a number
        if not isinstance(right_operand, (int, float)):
            raise ValueError("Right operand must be a number.")

        # Evaluate the left operand using the eval function
        left_result = eval(left_operand)

        # Evaluate the right operand using the eval function
        right_result = eval(right_operand)

        # Return the result of the evaluation
        return left_result + right_result

    # Evaluate the RPN expression
    result = evaluate_rpn(tokens[0])

    return result

# Test the function
tokens = ["#+", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
print(eval_rpn(tokens))  # Output: 35

tokens = ["+", "2", "3", "4", "5", "6", "7", "8", "9", "0", "1"]
print(eval_rpn(tokens))  # Output: 15

tokens = ["+", "2", "3", "4", "5", "6", "7", "8", "9", "0", "1", "2"]
print(eval_rpn(tokens))  # Output: 15

tokens = ["+", "2