# CHECK_TOKEN: LRUCache

```python
class LRUCache:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.cache = {}

    def get(self, key: str) -> int:
        if key in self.cache:
            return self.cache[key]
        self.cache[key] = self._get_or_create(key)
        return self.cache[key]

    def put(self, key: str, value: int) -> None:
        if key in self.cache:
            self.cache[key] = self._get_or_create(key)
        else:
            self.cache[key] = value
            self._put(key, value)

    def _get_or_create(self, key: str) -> int:
        if key in self.cache:
            return self.cache[key]
        value = self._get(key)
        if value is None:
            self.cache[key] = value
        return value

    def _put(self, key: str, value: int) -> None:
        if key in self.cache:
            self.cache[key] = self.cache.pop(key)
        else:
            self.cache[key] = value
```

Explanation:
- The `LRUCache` class is defined with the `__init__` method, which initializes an empty dictionary `self.cache` to store the cache entries.
- The `get` method takes a key as input and returns the value associated with that key if it exists in the cache. If the key is not found in the cache, it calls the `_get_or_create` method to either retrieve the value from the cache or create a new entry with the given key and its initial value.
- The `_get_or_create` method checks if the key is already present in the cache. If it is, it returns the existing value. If the key is not present, it calls the `_get` method to retrieve the value from the cache and returns it. If the value is not found, it creates a new entry with the given key and its initial value.
- The `put` method takes a key and a value as input and updates the corresponding value in the cache. If the key is already present in the cache, it updates the existing value. If the key is not present, it creates a new entry with the given key and its initial value, and then calls the `_put` method to update the cache.
- The `_put` method first