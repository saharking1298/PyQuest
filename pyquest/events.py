import random
import re


class Event:
    def __init__(self, event=None, _next=None, **config):
        self.next = _next
        if type(event) == str:
            if event.startswith("$"):
                event = CustomEvent(event[1:])
            elif event.startswith("@"):
                event = NamedEvent(event[1:])
            else:
                event = Prompt(event)
        elif type(event) in (list, tuple):
            event = PromptCarousel(event)
        self.event = event
        self.config = config

    def __str__(self):
        return f"event: {self.event}\nnext: {self.next}"

    def __repr__(self):
        return self.__str__()

class CustomEvent:
    def __init__(self, name):
        self.name = name


class NamedEvent:
    def __init__(self, name):
        self.name = name


class Teleporter:
    def __init__(self, room, event=None):
        self.room = room
        self.event = Event(event)


class Chain:
    def __init__(self, *args):
        args = list(args)
        for i in range(len(args)):
            args[i] = Event(args[i])
        self.events = args


class Conditional:
    def __init__(self, flag_name, options):
        self.flag = flag_name
        self.options = {}
        if type(options) == dict:
            for (name, value) in options.items():
                self.options[name] = Event(value)
        else:
            self.options = {}

    def get(self, flag_value):
        number = re.compile(r"\d+$")
        above = re.compile(r">\d+$")
        below = re.compile(r"<\d+$")
        above_equal = re.compile(r">=\d+$")
        below_equal = re.compile(r"<=\d+$")
        not_equal = False
        string = ""
        # Options: n, <>=n, 'str'
        for (name, value) in self.options.items():
            if name.startswith("!"):
                not_equal = True
                name = name.split("!", 1)[1]
                if number.match(name) is not None:
                    if int(name) != flag_value:
                        return value
            if name.startswith("'") and name.endswith("'") and len(name) > 1:
                string = name[1:-1]
            elif number.match(name) is not None:
                if int(name) == flag_value:
                    return value
            elif name == "true" and flag_value is True:
                return value
            elif name == "false" and flag_value is False:
                return value
            elif name == "null" and flag_value is None:
                return value
            elif above.match(name) is not None:
                if flag_value > int(name[1:]):
                    return value
            elif below.match(name) is not None:
                if flag_value < int(name[1:]):
                    return value
            elif above_equal.match(name) is not None:
                if flag_value >= int(name[2:]):
                    return value
            elif below_equal.match(name) is not None:
                if flag_value <= int(name[2:]):
                    return value

            if string != "":
                if not_equal:
                    if flag_value != name:
                        return value
                else:
                    if flag_value == name:
                        return value
        return Event()


class Manipulator:
    def __init__(self, manipulators, event=None):
        self.event = Event(event)
        self.manipulators = {}
        if type(manipulators) == dict:
            self.manipulators = manipulators

    def manipulate(self, flag, flag_value):
        manipulator = self.manipulators[flag]
        if isinstance(manipulator, Random):
            manipulator = random.randint(manipulator.min, manipulator.max)
        if type(manipulator) != str:
            return manipulator

        number = re.compile(r"\d+$")
        add = re.compile(r"\+\d+$")
        sub = re.compile(r"-\d+$")
        negative = re.compile(r"=-\d+$")
        if manipulator == "null":
            return None
        elif manipulator == "true":
            return True
        elif manipulator == "false":
            return False
        elif manipulator.startswith("'") and manipulator.endswith("'") and len(manipulator) > 1:
            return manipulator[1:-1]
        elif number.match(manipulator) is not None:
            return int(manipulator)
        elif negative.match(manipulator):
            return int(manipulator[1:])
        elif add.match(manipulator) is not None:
            return flag_value + int(manipulator[1:])
        elif sub.match(manipulator) is not None:
            return flag_value - int(manipulator[1:])


class Prompt:
    def __init__(self, prompt):
        self.prompt = prompt


class PromptCarousel:
    def __init__(self, prompts, shuffle=True, repeat=True):
        if type(prompts) in (list, tuple):
            self.prompts = prompts
        else:
            self.prompts = []
        self.current = 0
        self.shuffle = shuffle
        self.repeat = repeat

    def next(self):
        if len(self.prompts) == 0:
            return
        current = self.current
        if current == 0 and self.shuffle:
            # Shuffle the prompts list
            backup = list(self.prompts[:-1])
            index = random.randint(1, len(backup))
            random.shuffle(backup)
            backup.insert(index, self.prompts[-1])
            self.prompts = backup
        self.current += 1
        if self.current == len(self.prompts):
            if self.repeat:
                self.current = 0
            else:
                self.current = current
        return self.prompts[current]


class Break:
    def __init__(self, event=None):
        self.event = Event(event)


class Menu:
    def __init__(self, starter, options, repeat=False):
        self.starter = Event(starter)
        self.repeat = repeat
        self.options = {}
        for (name, value) in options.items():
            self.options[name] = Event(value)


class Random:
    def __init__(self, minimum, maximum=None):
        if maximum is None:
            self.min = 0
            self.max = minimum
        else:
            self.min = minimum
            self.max = maximum


class Lock:
    def __init__(self, flag, success=None, failure=None, final=None):
        self.success = Event(success)
        self.failure = Event(failure)
        self.final = Event(final)
        self.flag = flag
