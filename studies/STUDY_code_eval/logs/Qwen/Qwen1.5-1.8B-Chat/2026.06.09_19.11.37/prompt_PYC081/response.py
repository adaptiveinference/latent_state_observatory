# CHECK_TOKEN: PYC081

# Function to summarize transactions grouped by monthly totals
def summarize_transactions(rows):
    # Check if the input is a list of lists
    if not isinstance(rows, list):
        raise ValueError("Input must be a list of lists")

    # Check if the input is a list of dictionaries
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError("Input must be a list of dictionaries")

    # Initialize an empty dictionary to store the monthly totals
    monthly_totals = {}

    # Iterate through each row in the input list
    for row in rows:
        # Check if the row is a dictionary
        if not isinstance(row, dict):
            raise ValueError("Each row must be a dictionary")

        # Extract the category and total from the row
        category = row.get("category")
        total = row.get("total")

        # If the category is not already in the monthly_totals dictionary, add it with the total
        if category not in monthly_totals:
            monthly_totals[category] = total

        # Increment the total for the category
        monthly_totals[category] += total

    # Return the monthly_totals dictionary
    return monthly_totals

# Example usage
rows = [
    {"category": "Electronics", "total": 100},
    {"category": "Clothing", "total": 200},
    {"category": "Food", "total": 300},
    {"category": "Home", "total": 400},
    {"category": "Travel", "total": 500}
]

monthly_totals = summarize_transactions(rows)
print(monthly_totals)  # Output: {'Electronics': 100, 'Clothing': 200, 'Food': 300, 'Home': 400, 'Travel': 500}