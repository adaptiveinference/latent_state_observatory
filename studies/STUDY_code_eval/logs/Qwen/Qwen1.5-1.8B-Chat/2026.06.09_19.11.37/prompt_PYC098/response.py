# CHECK_TOKEN: PYC098

# Function to paginate a list of items and return a list of pages
def paginate(items, page_size):
    # Check if the page_size is a positive integer
    if not isinstance(page_size, int) or page_size <= 0:
        raise ValueError("Page size must be a positive integer")

    # Initialize an empty list to store the pages
    pages = []

    # Iterate over the items in reverse order
    for i in range(len(items) - page_size + 1):
        # Calculate the index of the current page
        page_index = i + page_size

        # Check if the current page is within the range of the items
        if page_index >= 0 and page_index < len(items):
            # Append the current item to the current page
            pages.append(items[page_index])
        else:
            # If the current page is out of range, append the first item of the next page
            pages.append(items[0])

    # Return the list of pages
    return pages

# Example usage
items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
page_size = 3

# Paginate the items and return the list of pages
pages = paginate(items, page_size)
print(pages)  # Output: [3, 4, 5]