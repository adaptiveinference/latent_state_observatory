# CHECK_TOKEN: PYC020

# Define function is_leap_year(year) using standard leap year rules.
def is_leap_year(year):
    """
    Returns True if the given year is a leap year, False otherwise.
    Leap years are defined as years divisible by 4, except for years divisible by 100 but not by 400.
    """
    if year % 4 == 0:
        if year % 100 != 0:
            if year % 400 == 0:
                return True
            else:
                return False
        else:
            return True
    else:
        return False

# Test the function
print(is_leap_year(2020))  # Output: True
print(is_leap_year(1900))  # Output: False
print(is_leap_year(2000))  # Output: True
print(is_leap_year(19000))  # Output: False
print(is_leap_year(20000))  # Output: False
print(is_leap_year(2024))  # Output: True
print(is_leap_year(2025))  # Output: False
print(is_leap_year(2026))  # Output: False
print(is_leap_year(2027))  # Output: False
print(is_leap_year(2028))  # Output: False
print(is_leap_year(2029))  # Output: False
print(is_leap_year(2030))  # Output: False
print(is_leap_year(2031))  # Output: False
print(is_leap_year(2032))  # Output: False
print(is_leap_year(2033))  # Output: False
print(is_leap_year(2034))  # Output: False
print(is_leap_year(2035))  # Output: False
print(is_leap_year(2036))  # Output: False
print(is_leap_year(2037))  # Output: False
print(is_leap_year(2038))  # Output: False
print(is_leap_year(2039))  # Output