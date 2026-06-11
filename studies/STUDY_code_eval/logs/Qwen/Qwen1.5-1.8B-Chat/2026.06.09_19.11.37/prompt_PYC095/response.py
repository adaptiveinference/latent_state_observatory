# CHECK_TOKEN: PYC095

# Implement the function parse_log_events to extract timestamp, level, and message dictionaries from a log event string
def parse_log_events(text):
    # Check if the text is a valid log event string
    if not text.startswith('#') or not text.endswith('#'):
        raise ValueError("Log event string must start with '#' and end with '#'")
    
    # Split the text into a list of log event tokens
    tokens = text.split('#')
    
    # Check if the number of tokens is equal to 3
    if len(tokens) != 3:
        raise ValueError("Log event string must contain exactly 3 tokens: timestamp, level, and message")
    
    # Extract the timestamp from the first token
    timestamp = tokens[0]
    
    # Extract the level from the second token
    level = tokens[1]
    
    # Extract the message from the third token
    message = tokens[2]
    
    # Return the extracted dictionaries
    return {"timestamp": timestamp, "level": level, "message": message}