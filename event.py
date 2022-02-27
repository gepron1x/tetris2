
class Signal:

    def __init__(self):
        self.listeners = set()

    def connect(self, func):
        self.listeners.add(func)

    def emit(self, *args, **kwargs):
        for listener in self.listeners:
            listener(*args, **kwargs)
