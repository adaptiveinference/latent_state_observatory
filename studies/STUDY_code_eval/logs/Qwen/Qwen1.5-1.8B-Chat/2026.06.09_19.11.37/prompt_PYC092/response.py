# CHECK_TOKEN: PYC092

# Function to train and test split rows using the train_test_split function from the sklearn.model_selection module
def train_test_split_rows(rows, test_fraction, seed):
    # Check if the input arguments are valid
    if not isinstance(rows, list) or not isinstance(test_fraction, float) or not isinstance(seed, int):
        raise ValueError("All input arguments must be of type list, float, and integer.")

    # Check if the test_fraction is within the valid range (0.2 to 1)
    if test_fraction < 0.2 or test_fraction > 1:
        raise ValueError("Test_fraction must be between 0.2 and 1.")

    # Check if the seed is within the valid range (0 to 2**31 - 1)
    if seed < 0 or seed > 2**31 - 1:
        raise ValueError("Seed must be between 0 and 2**31 - 1.")

    # Split the rows into training and testing sets
    train_size = int(len(rows) * test_fraction)
    train_set = rows[:train_size]
    test_set = rows[train_size:]

    # Shuffle the training set randomly
    random.shuffle(train_set)

    # Split the test set into training and validation sets
    test_size = int(len(test_set) * test_fraction)
    train_val_set = train_set[:test_size]
    val_set = test_set[test_size:]

    # Create an instance of the train_test_split function
    train_test_split = train_test_split(train_set, test_size, seed)

    return train_test_split

# Example usage
rows = [1, 2, 3, 4, 5]
test_fraction = 0.3
seed = 42

# Train and test split the rows
train_test_split = train_test_split_rows(rows, test_fraction, seed)
print("Training set:")
print(train_test_split)

# Validate the split
val_set = train_test_split.val_set
print("Validation set:")
print(val_set)