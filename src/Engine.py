from Core import Prompt, PromptCarousel, Room
from Events import Event, CustomEvent, Conditional, Manipulator, NamedEvent
import re


class Engine:
    def __init__(self, events_handler, starting_room):
        self.currentRoom = starting_room
        self.events_handler = events_handler
        self.prompts = {
            "start": "Welcome to SaharSword\n"
                     "Type 'help' to get a list of valid commands.\n",
            "help": "Type 'help [command]' to get info on a specific command.\n"
                    "List of available commands:",
            "inputError": "Unknown action or keyword.",
        }
        self.commands = {
            "go": "Move to a certain direction.\n"
                  "Valid directions: north, south, west, east, up, down, in,"
                  " out.\nSyntax: go [direction]",
            "enter": "Enter a certain location. "
                     "To see a list of locations, use 'map' command.\n"
                     "Usage: 'enter [locationName]'.",
            "look": "Look at the room or a specific item. "
                    "To look at an item, type the item's name.\n"
                    "Syntax: look [item]",
            "map": "Display a list of all locations and directions "
                   "you can go to.\n"
                   "Identical commands: 'locations', 'directions'",
            "use": "Activate an interactive. Use 'map' command to see a list of "
                   "all interactives.\n Syntax: 'use [interactiveName]'."
                   "\nIdentical commands: 'activate'.",
            "inventory": "See the contents of your inventory. "
                         "Identical commands: 'backpack', 'i'."
        }
        self.match = {
            "exit": self.quit,
            "quit": self.quit,
        }
        self.keywords = {
            "go": self.command_go,
            "enter": self.command_enter,
            "help": self.command_help,
            "use": self.command_use,
            "activate": self.command_use,
            "look": self.command_look,
            "map": self.command_map,
        }
        self.flags = {}
        self.events = {}

    def print(self, *args):
        print(*args)

    def quit(self):
        self.print("Goodbye!")
        exit(0)

    def custom_event(self, event_name):
        if type(self.events_handler) == dict:
            if event_name in self.events_handler:
                if callable(self.events_handler[event_name]):
                    self.events_handler[event_name]()
        elif callable(self.events_handler):
            self.events_handler(event_name)

    def handle_event(self, wrapper):
        event = wrapper.event
        if isinstance(event, Conditional):
            self.handle_event(event.get(self.flags[event.flag]))
        elif isinstance(event, Manipulator):
            self.handle_event(event.event)
            self.flags[event.flag] = event.manipulate(self.flags[event.flag])
        elif isinstance(event, CustomEvent):
            self.custom_event(event.name)
        elif isinstance(event, NamedEvent):
            if event.name in self.events:
                self.handle_event(Event(event=self.events[event.name]))
        elif isinstance(event, Prompt):
            self.print(event.prompt)
        elif isinstance(event, PromptCarousel):
            self.print(event.next())
        if isinstance(wrapper.next, Room):
            self.set_current_room(wrapper.next)

    def set_current_room(self, room):
        self.currentRoom = room
        self.show_prompt()

    def command_enter(self, _next):
        _map = self.currentRoom.map
        if _next in _map.get_all():
            self.handle_event(_map.get(_next))

    def command_go(self, _next):
        compass = self.currentRoom.compass
        result = compass.get(_next)
        if result is None:
            self.print("You can't go there!")
            return True
        elif result is False:
            self.print(f"No such direction: '{_next}'.")
            return True
        else:
            self.handle_event(compass.get(_next))

    def command_help(self, _next):
        if _next == "":
            self.print(self.prompts["help"])
            for command in self.commands:
                self.print("- " + command)
        else:
            found = False
            for command in self.commands:
                if _next == command:
                    self.print(f"---- {command}: Command Description ----\n"
                               f"{self.commands[command]}")
                    found = True
                    break
            if not found:
                self.print(f"No such command: '{_next}'.")
        return True

    def command_look(self, _next):
        if _next in ("around", ""):
            self.print("You look around.")
            return True
        triggers = ["on the", "at the", "at", "on"]
        for trigger in triggers:
            if _next.startswith(trigger):
                _next = _next.split(trigger, 1)[1].strip()
        interactive = self.currentRoom.interactives.get(_next)
        if interactive is None:
            self.print(f"No such object: '{_next}'.")
        else:
            self.print(f"You look at the {_next}.\n{interactive.description}")

    def command_map(self, _next=""):
        room = self.currentRoom
        if len(room.compass) > 0:
            self.print("You can go: " + ", ".join(room.compass.get_all(True)))
        if len(room.map) > 0:
            self.print("You can enter: " + ", ".join(room.map.get_all(True)))
        if len(room.interactives) > 0:
            self.print("You can activate: " + ", ".join(room.interactives.get_all(True)))
        if len(room.items) > 0:
            self.print("You can take: " + ", ".join(room.items.get_all(True)))

    def command_use(self, _next):
        room = self.currentRoom
        interactives = room.interactives.get_all()
        if _next in interactives:
            event = room.interactives.get(_next).events["activate"]
            if isinstance(event, Event):
                self.handle_event(event)
            else:
                print("Warning 001")
        else:
            self.print(f"No such interactive: '{_next}'.")

    def show_prompt(self):
        self.print(self.currentRoom.description)
        self.command_map()

        self.handle_input()

    def handle_input(self):
        show_prompt = False
        while True:
            user_input = input().lower().strip()
            user_input = re.sub(" +", " ", user_input)
            if user_input == "":
                continue
            if user_input in self.match:
                self.match[user_input]()
                break
            words = user_input.split(" ", 1)
            keyword = words[0]
            _next = ""
            if len(words) > 1:
                _next = words[1]
            if keyword in self.keywords:
                show_prompt = self.keywords[keyword](_next)
                break
            else:
                self.print(self.prompts["inputError"])
        if show_prompt:
            self.print()
            self.show_prompt()
        else:
            self.handle_input()

    def start(self):
        self.show_prompt()
