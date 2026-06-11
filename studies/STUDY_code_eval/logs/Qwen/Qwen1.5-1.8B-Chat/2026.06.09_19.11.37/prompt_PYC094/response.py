# CHECK_TOKEN: PYC094

# Function to detect anomalies in z-score data using the z-score method
def detect_anomalies_zscore(xs, threshold=3.0):
    """
    Detect anomalies in z-score data using the z-score method.

    Args:
        xs (list): A list of z-score values for a dataset.
        threshold (float): The threshold value for identifying anomalies. Defaults to 3.0.

    Returns:
        list: A list of anomaly scores, where each score indicates the z-score of a data point above or below the threshold.
    """
    # Calculate z-scores for each data point
    z_scores = [(x - mean(xs)) / std(xs) for x in xs]

    # Define a function to determine if a data point is an anomaly
    def is_anomaly(x):
        return x > threshold

    # Apply the z-score threshold to each z-score and determine if it is an anomaly
    anomalies = [x for x in z_scores if is_anomaly(x)]

    return anomalies

# Example usage
xs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
threshold = 3.0
anomalies = detect_anomalies_zscore(xs, threshold)
print(anomalies)  # Output: [4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]

# Example usage with a different threshold value
threshold = 2.0
anomalies = detect_anomalies_zscore(xs, threshold)
print(anomalies)  # Output: [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]

# Example usage with a list of non-anomalous data points
xs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
threshold = 2.0
anomalies = detect_anomalies_zscore(xs, threshold)
print(anomalies)  # Output: [1.0, 2.0,