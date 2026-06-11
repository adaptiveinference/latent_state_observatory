# CHECK_TOKEN: Counter

class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1

    def decrement(self):
        if self.value > 0:
            self.value -= 1
        else:
            print("Value cannot be negative.")

    def value(self):
        return self.value

# Example usage:
counter = Counter()
counter.increment()
counter.increment()
counter.decrement()
print(counter.value())  # Output: 2

counter.decrement()
print(counter.value())  # Output: 1

counter.increment()
counter.increment()
counter.decrement()
print(counter.value())  # Output: 0

counter.decrement()
print(counter.value())  # Output: -1

counter.decrement()
print(counter.value())  # Output: "Value cannot be negative."