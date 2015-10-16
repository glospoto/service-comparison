"""
This class implements an Observable object, in accord with Observer pattern. In this implementation, a notify_all
method takes two arguments: command and path. A command specifies if rule has to be installed or removed (in accord
with constants specified in ofp/command.py), whereas path is the path calculated by PolicyPathSearcher instance.
"""


class Observable(object):

    def __init__(self):
        # The list of observers' objects
        self._observers = []

    # Add an observer to this observable object
    def add_observer(self, observer):
        if not observer in self._observers:
            self._observers.append(observer)

    # Remove an observer from this observable object
    def remove_observer(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    # Notify all observers of this object
    def notify_all(self):
        for observer in self._observers:
            observer.update()
