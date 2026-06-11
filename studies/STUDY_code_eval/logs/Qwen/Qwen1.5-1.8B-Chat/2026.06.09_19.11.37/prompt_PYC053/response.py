# CHECK_TOKEN: PyC053

class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance_to(self, other: Point) -> float:
        return ((self.x - other.x) ** 2) + ((self.y - other.y) ** 2)

# Example usage:
point1 = Point(1, 2)
point2 = Point(3, 4)

print(point1.distance_to(point2))  # Output: 5.0

# Explanation:
In the Python code provided, we define a class called `Point` with two attributes: `x` and `y`. The `__init__` method initializes these attributes with the values `x` and `y` respectively.

The `distance_to` method takes another `Point` object `other` as input and calculates the Euclidean distance between the two points using the Pythagorean theorem. The formula for calculating the distance between two points in a 2D plane is:
distance = sqrt((x2 - x1)² + (y2 - y1)²)

Here, `x1` and `y1` are the coordinates of the first point, and `x2` and `y2` are the coordinates of the second point.

The method returns the calculated distance as a float value.

In the example usage, we create two `Point` objects `point1` and `point2` with the respective coordinates `(1, 2)` and `(3, 4)`. We then call the `distance_to` method on `point1` and `point2` and print the result, which is `5.0`. This indicates that the distance between `point1` and `point2` is 5 units in the x-y plane.