# CHECK_TOKEN: PYC096

```python
class EventEmitter:
    def __init__(self):
        self.events = {}

    def on(self, event_name, callback):
        self.events[event_name] = callback

    def off(self, event_name):
        if event_name in self.events:
            del self.events[event_name]

    def emit(self, event_name, data):
        if event_name in self.events:
            self.events[event_name].emit(data)
```

Explanation:
The `EventEmitter` class is a Python class that represents an event listener. It has three methods:

1. `__init__`: This method initializes an empty dictionary `events` to store event names and their corresponding callback functions. The `events` dictionary is used to store the event names as keys and the callback functions as values.

2. `on`: This method takes an event name and a callback function as arguments. It adds the callback function to the `events` dictionary with the event name as the key and the callback function as the value. If the event name is not already present in the `events` dictionary, it creates a new key-value pair with the event name as the key and the callback function as the value.

3. `off`: This method takes an event name as an argument. It checks if the event name is present in the `events` dictionary. If it is, it deletes the corresponding callback function from the `events` dictionary using the `del` statement.

4. `emit`: This method takes an event name and a data parameter as arguments. It checks if the event name is present in the `events` dictionary. If it is, it calls the callback function associated with the event name with the data parameter using the `emit` method of the `events` dictionary.

Example usage:
```python
emitter = EventEmitter()

emitter.on('event1', lambda data: print(f'Event 1 emitted: {data}'))
emitter.on('event2', lambda data: print(f'Event 2 emitted: {data}'))
emitter.on('event3', lambda data: print(f'Event 3 emitted: {data}'))

emitter.off('event1')
emitter.emit('event1', 'Hello, world!')
emitter.emit('event2', 'Hello, world!')
emitter.emit('event3', 'Hello, world!')

emitter.off('event2')
emitter.emit('event1