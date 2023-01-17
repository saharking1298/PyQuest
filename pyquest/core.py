from .errors import DirectionError
from .config import defaults
from .events import Event


class _Compass:
    def __init__(self):
        directions = (
            "north",
            "south",
            "east",
            "west",
            "up",
            "down",
            "in",
            "out"
        )
        self.data = {}
        for direction in directions:
            self.data[direction] = None

    def __len__(self):
        return len(self.get_all(prompt=True))

    def set(self, direction, destination, event=None, hidden=False):
        direction = direction.lower().strip()
        for item in self.data:
            if item == direction:
                self.data[item] = Event(event, destination, hidden=hidden)
                return
        raise DirectionError("Undefined direction: " + direction)

    def get(self, direction):
        if len(direction) == 1:
            for item in self.data:
                if item.startswith(direction):
                    return self.data[item]
        else:
            for item in self.data:
                if item == direction:
                    return self.data[direction]
        return False

    def get_all(self, prompt=False):
        result = []
        for (name, value) in self.data.items():
            if value is not None and (not prompt or not value.config["hidden"]):
                result.append(name)
        return result

    def remove(self, direction):
        self.set(direction, None)


class _Map:
    def __init__(self):
        self.data = {}

    def __len__(self):
        return len(self.get_all(prompt=True))

    def set(self, location, destination, event=None, hidden=False):
        if destination is None:
            del self.data[location]
        else:
            self.data[location] = Event(event, destination, hidden=hidden)

    def get(self, location):
        if location in self.data:
            return self.data[location]

    def get_all(self, prompt=False):
        result = []
        for (name, value) in self.data.items():
            if not prompt or not value.config["hidden"]:
                result.append(name)
        return result

    def remove(self, direction):
        self.set(direction, None)


class _Interactives:
    def __init__(self):
        self.data = []

    def __len__(self):
        return len(self.get_all(prompt=True))

    def add(self, *interactives):
        for interactive in interactives:
            added = False
            for i in range(len(self.data)):
                if self.data[i].name == interactive.name:
                    self.data[i] = interactive
                    added = True
            if not added:
                self.data.append(interactive)

    def get(self, name):
        for interactive in self.data:
            if interactive.name == name:
                return interactive

    def get_all(self, prompt=False):
        result = []
        for interactive in self.data:
            if not prompt or not interactive.hidden:
                result.append(interactive.name)
        return result

    def remove(self, name):
        for i in range(len(self.data)):
            if self.data[i].name == name:
                del self.data[i]


class _Items:
    def __init__(self):
        self.data = []

    def __len__(self):
        return len(self.get_all())

    def add(self, item):
        if not isinstance(item, Event):
            self.data.append(Event(item))
        else:
            self.data.append(item)

    def get_all(self):
        result = []
        for item in self.data:
            result.append(item.next.name)
        return result


class Interactive:
    def __init__(self, name, description="", activate=None, inspect=None, hidden=False):
        if description == "":
            description = defaults.prompts["interactive.description"]
        self.name = name
        self.description = Event(description)
        self.hidden = hidden
        self.events = {
            "interactive.inspect": Event(inspect),
            "interactive.activate": Event(activate)
        }

    def set(self, name, value):
        self.events[name] = Event(value)


class Room:
    def __init__(self, description, enter=None, leave=None, show_map=False):
        self.description = Event(description)
        self.compass = _Compass()
        self.map = _Map()
        self.interactives = _Interactives()
        self.items = _Items()
        self.show_map = show_map
        self.events = {
            "room.enter": Event(enter),
            "room.leave": Event(leave),
        }

    def is_empty(self):
        return len(self.map) == 0 and len(self.compass) == 0 and len(self.interactives) == 0 and len(self.items) == 0
