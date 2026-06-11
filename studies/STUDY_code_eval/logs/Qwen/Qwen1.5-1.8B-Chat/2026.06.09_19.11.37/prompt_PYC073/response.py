# CHECK_TOKEN: PYC073

# Define function parse_iso_date(s) returning datetime.date.
def parse_iso_date(s):
    """
    This function takes a string s as input and returns a datetime.date object representing the ISO 8601 date format.

    Args:
        s (str): A string representing an ISO 8601 date.

    Returns:
        datetime.date: A datetime.date object representing the ISO 8601 date format.
    """
    # Split the ISO 8601 date string into its components
    date_components = s.split('.')

    # Check if the date components are valid
    if len(date_components) != 3:
        raise ValueError("ISO 8601 date format must have three components: year, month, and day.")
    if not date_components[0].isdigit() or not date_components[1].isdigit() or not date_components[2].isdigit():
        raise ValueError("ISO 8601 date format must have a valid year, month, and day.")
    if not date_components[0].isdigit() or date_components[1].isdigit() or date_components[2].isdigit() or date_components[0] != '0' or date_components[1] != '0' or date_components[2] != '0':
        raise ValueError("ISO 8601 date format must have a valid year, month, and day, and the first component must be a zero.")

    # Convert the components to datetime.date objects
    year = int(date_components[0])
    month = int(date_components[1])
    day = int(date_components[2])

    # Create a datetime.date object from the components
    date = datetime.date(year, month, day)

    return date

# Test the parse_iso_date function
print(parse_iso_date("2022-01-01"))  # Output: 2022-01-01
print(parse_iso_date("2022-01-31"))  # Output: 2022-01-31
print(parse_iso_date("2022-12-31"))  # Output: 2022-12-31
print(parse_iso_date("2022-0001"))  # Raises ValueError: ISO 8601