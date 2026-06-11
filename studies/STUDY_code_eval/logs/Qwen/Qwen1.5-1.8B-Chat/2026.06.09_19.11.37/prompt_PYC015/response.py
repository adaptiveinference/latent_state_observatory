# CHECK_TOKEN: PYC015

# Define function letter_grade(score) returning A/B/C/D/F.

def letter_grade(score):
    # Check if the score is a positive integer
    if not isinstance(score, int) or score <= 0:
        raise ValueError("Score must be a positive integer.")
    
    # Check if the score is within the range of 0-100
    if score < 0 or score > 100:
        raise ValueError("Score must be between 0 and 100.")
    
    # Check if the score is a whole number
    if not score.is_integer():
        raise ValueError("Score must be a whole number.")
    
    # Calculate letter grade based on the score
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    elif score >= 50:
        return "F"
    else:
        return "Invalid score. Please provide a score between 0 and 100."