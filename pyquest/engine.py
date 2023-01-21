from .events import Chain, NamedEvent, Prompt, PromptCarousel, Menu, Teleporter
from .events import Event, CustomEvent, Conditional, Manipulator, Break, Lock
from .core import Room
from .config import defaults
import re


class Printer:
    def __init__(self):
        pass

    def print(self, *args):
        print(*args)


class Engine:
    def __init__(self, events_handler: callable = None, starting_room: Room = None, npc_handler: callable = None):
        self.currentRoom = starting_room
        self.eventHandler = events_handler
        self.npcHandler = npc_handler
        self.printer = Printer()
        self.run = True

        self.commands = {
            "go": self.command_go,
            "enter": self.command_enter,
            "help": self.command_help,
            "use": self.command_use,
            "activate": self.command_use,
            "look": self.command_look,
            "map": self.command_map,
            "talk": self.command_talk,
            "quit": self.quit,
        }
        self.aliases = {
            "exit": "quit",
            "inspect": "look",
            "locations": "map",
            "chat": "talk"
        }
        self.flags = {}
        self.events = {}
        self.last_input = ""
        self.prompt = False

    def render(self, namespace, name, *args, output=True):
        valid_namespaces = ("prompts", "errors", "commands")
        if namespace not in valid_namespaces:
            namespace += "s"
        if namespace in valid_namespaces:
            text = defaults.data[namespace][name]
            if len(args) > 0:
                text = text.format(*args)
            if output:
                self.print(text)
            return text

    def print(self, *args: str):
        if len(args) > 0 and type(args[0]) == str and args[0].startswith("$"):
            base = defaults.get(args[0])
            if base is None:
                self.printer.print(*args)
            else:
                if len(args) > 1:
                    args = args[1:]
                    self.printer.print(base.format(*args))
                else:
                    self.printer.print(base)
        else:
            self.printer.print(*args)

    def quit(self, _next: str = ""):
        if _next in ("game", ""):
            self.render("prompt", "game.quit")
            self.run = False
        else:
            self.render("error", "input.invalid")
        
    def custom_event(self, event_name):
        if type(self.eventHandler) == dict:
            if event_name in self.eventHandler:
                if callable(self.eventHandler[event_name]):
                    self.eventHandler[event_name]()
        elif callable(self.eventHandler):
            self.eventHandler(event_name)

    def handle_event(self, wrapper):
        event = wrapper.event
        if isinstance(wrapper.next, Room):
            self.handle_event(self.currentRoom.events["room.leave"])
        if isinstance(event, Chain):
            for e in event.events:
                self.handle_event(e)
        elif isinstance(event, Conditional):
            self.handle_event(event.get(self.flags[event.flag]))
        elif isinstance(event, Manipulator):
            self.handle_event(event.event)
            for flag in event.manipulators:
                self.flags[flag] = event.manipulate(flag, self.flags[flag])
        elif isinstance(event, CustomEvent):
            self.custom_event(event.name)
        elif isinstance(event, NamedEvent):
            if event.name in self.events:
                self.handle_event(Event(self.events[event.name]))
        elif isinstance(event, Prompt):
            prompt = self.parse_prompt(event.prompt)
            self.print(prompt)
        elif isinstance(event, PromptCarousel):
            prompt = self.parse_prompt(event.next())
            self.print(prompt)
        elif isinstance(event, Menu):
            self.show_menu(event)
            self.prompt = True
        elif isinstance(event, Teleporter):
            self.handle_event(event.event)
            self.change_room(event.room, True)
        elif isinstance(event, Lock):
            if self.flags[event.flag] is False:
                self.handle_event(event.success)
                self.handle_event(event.final)
            elif self.flags[event.flag] is True:
                self.handle_event(event.failure)
                self.handle_event(event.final)
                self.prompt = True
                return
        if isinstance(wrapper.next, Room):
            self.change_room(wrapper.next)

    def change_room(self, room, trigger_leave=False):
        if trigger_leave:
            self.handle_event(self.currentRoom.events["room.leave"])
        self.currentRoom = room
        self.handle_event(self.currentRoom.events["room.enter"])
        self.show_prompt()

    def parse_prompt(self, prompt):
        if prompt.count("}") > 0 and prompt.count("{") > 0:
            for (name, value) in self.flags.items():
                filler = "{" + str(name) + "}"
                prompt = prompt.replace(filler, str(value))
        return prompt

    def show_menu(self, menu):
        flag = True
        number = re.compile(r"\d+$")
        choice = 0
        while flag:
            self.handle_event(menu.starter)
            for i in range(len(menu.options)):
                self.print(f"{i+1}. {self.parse_prompt(tuple(menu.options.keys())[i])}")
            while True:
                user_input = input().strip()
                if user_input == "":
                    continue
                if number.match(user_input) is not None:
                    choice = int(user_input)
                    if 0 < choice <= len(menu.options):
                        choice -= 1
                        break
                self.render("error", "menu.choice.invalid")
            event = tuple(menu.options.values())[choice]
            if not menu.repeat:
                flag = False
            if isinstance(event.event, Break):
                flag = False
                event = event.event.event
            self.handle_event(event)
            if flag:
                self.print()

    def command_enter(self, _next: str):
        found = False
        _map = self.currentRoom.map
        if _next in _map.get_all():
            event = _map.get(_next)
            if event.event is None:
                event.event = Prompt(self.render("prompt", "map.move", _next, output=False))
            self.handle_event(event)

            self.handle_event(_map.get(_next))
            self.prompt = True
            found = True
        if not found:
            self.render("error", "map.notFound", _next)

    def command_go(self, _next: str):
        compass = self.currentRoom.compass
        result = compass.get(_next)
        if result is None:
            self.render("error", "compass.direction.invalid")
            self.prompt = True
        elif result is False:
            self.render("error", "compass.direction.notFound", _next)
            self.prompt = True
        else:
            event = compass.get(_next)
            if event.event is None:
                event.event = Prompt(self.render("prompt", "compass.move", _next, output=False))
            self.handle_event(event)

    def command_help(self, _next: str):
        if _next == "":
            self.render("prompts", "game.help")
            for command in defaults.commands:
                self.print("- " + command)
        else:
            found = False
            for command in defaults.commands:
                if _next == command:
                    self.render("prompt", "help.command.description", command.title())
                    self.print(defaults.commands[command])
                    found = True
                    break
            if not found:
                self.render("prompt", "help.command.notFound", _next)
        self.prompt = True

    def command_look(self, _next: str):
        if _next in ("around", ""):
            self.render("prompt", "room.inspect")
            self.prompt = True
            return
        triggers = ["on the", "at the", "at", "on"]
        for trigger in triggers:
            if _next.startswith(trigger):
                _next = _next.split(trigger, 1)[1].strip()
        interactive = self.currentRoom.interactives.get(_next)
        if interactive is None:
            self.render("error", "interactive.notFound", _next)
        else:
            self.render("prompt", "game.inspect", _next)
            self.handle_event(interactive.description)
            self.prompt = True

    def command_map(self, _next: str = ""):
        room = self.currentRoom
        if room.is_empty():
            self.render("prompt", "room.empty")
        else:
            if len(room.compass) > 0:
                locations = ", ".join(room.compass.get_all(True))
                self.render("prompt", "room.contents.compass", locations)
            if len(room.map) > 0:
                locations = ", ".join(room.map.get_all(True))
                self.render("prompt", "room.contents.map", locations)
            if len(room.npcs) > 0:
                locations = ", ".join(room.npcs.get_all(True))
                self.render("prompt", "room.contents.npcs", locations)
            if len(room.interactives) > 0:
                locations = ", ".join(room.interactives.get_all(True))
                self.render("prompt", "room.contents.interactives", locations)
            if len(room.items) > 0:
                locations = ", ".join(room.items.get_all(True))
                self.render("prompt", "room.contents.items", locations)

    def command_use(self, _next: str):
        room = self.currentRoom
        interactives = room.interactives.get_all()
        print(interactives)
        if _next in interactives:
            event = room.interactives.get(_next).events["interactive.activate"]
            if isinstance(event, Event):
                self.handle_event(event)
                self.prompt = True
        else:
            self.render("error", "interactive.notFound", _next)

    def command_talk(self, _next: str):
        removals = ("to", "with", "the")
        for entry in removals:
            entry += " "
            if _next.startswith(entry):
                _next = _next.replace(entry, "", 1)
        npc = self.currentRoom.npcs.get(_next)
        if npc is None:
            self.render("error", "npc.notFound", _next)
        else:
            self.print(npc.prompt())
            text = None
            while text != "":
                if text is not None:
                    self.print(self.npcHandler(npc, text))
                text = input(self.render("prompt", "npc.conversation", output=False))
            self.prompt = True

    def show_prompt(self):
        self.prompt = False
        self.handle_event(self.currentRoom.description)
        if self.currentRoom.showLocations:
            self.command_map()
        self.handle_input()

    def handle_input(self):
        # Allows quitting the game
        if not self.run:
            return

        # User input loop
        while True:
            # Taking user input
            user_input = input().lower().strip()
            # Building a list of words
            user_input = re.sub(" +", " ", user_input)
            # If there is no input, continue
            if user_input == "":
                continue
            # Special syntax for repeating the last input
            elif user_input == "_":
                user_input = self.last_input
            self.last_input = user_input
            # command = command, the first word
            # _next   = arguments, the following words
            words = user_input.split(" ", 1)
            command = words[0]
            _next = ""
            if len(words) > 1:
                _next = words[1]
            # If input is a valid command, execute that command (help, map, etc.)
            if command in self.commands:
                self.commands[command](_next)
                break
            # Command can also be an alias
            elif command in self.aliases:
                self.commands[self.aliases[command]](_next)
                break
            # Otherwise, show an input error
            else:
                self.render("error", "input.invalid")
        # Prints the current room's prompt if needed
        if self.prompt:
            self.print()
            self.show_prompt()
        # Otherwise, repeats this very function
        else:
            self.handle_input()

    def start(self, starting_room: Room = None) -> None:
        # Setting starting room
        if starting_room is not None:
            self.currentRoom = starting_room
        # Printing the starting prompt
        self.render("prompt", "game.start")
        # Starting mainloop
        self.show_prompt()
