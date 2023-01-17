from pyquest import Room, Interactive
from pyquest import Conditional, Manipulator, Chain, Menu, Break, Teleporter, Random, Lock
from pyquest import Engine
# Defining flags
flags = {
    "player.isSitting": False,
    "inters.tv.on": False,
    "rooms.attic.isLocked": True,
    "inters.trampoline.rand": 0,
    "flags.fbi": False,
    "fillers.fbi": "",
}
# Defining events
events = {
    "inters.couch.getUp": Conditional(
        "player.isSitting",
        {
            "true": Manipulator(
                {"player.isSitting": False},
                "You get up from the couch."
            )
        }
    ),
    "inters.couch.sit": Manipulator(
        {"player.isSitting": True},
        "You sit on the couch."
    ),
    "room.leave": Chain(
        "@inters.couch.getUp",
    ),
    "inters.tv.turnOff": Manipulator({"inters.tv.on": False})
}
# Building rooms
rooms = {
    "outside": Room(
        "You stand outside your house.\n"
        "What are you waiting for? Enter the house."
    ),
    "house.livingRoom": Room(
        "You are at the house living room. \n" 
        "A couch stands in front of a coffee table and a 50 inch television.\n" 
        "You can enter the kitchen, the guest room and the garden.\n" 
        "You can also take the stairs and go up to the second floor, "
        "or leave the house and go out.",
        leave="@room.leave"
    ),
    "house.garden": Room(
        "The garden is breathtaking, with green grass and flowers all around.\n"
        "A huge trampoline is in the center of the garden, waiting to be jumped on.\n"
        "You can enter back into the house."
    ),
    "house.kitchen": Room(
        "The kitchen is accessorized with a fridge, "
        "oven with stove and a sink with some dirty dishes.\n"
        "There is also a dining table you can eat on.\n"
        "You can go out to the living room."
    ),
    "house.guestRoom": Room(
        "This is a usual guest room - with a couch, a bed and a mini bar.\n"
        "When you have guests overnight they stay here.\n"
        "You can go out to the living room.",
        leave="@room.leave"
    ),
    "house.hallway": Room(
        "You are at the hallway of the house second floor.\n"
        "You can enter the bedroom, bathroom and balcony, "
        "or take the stairs and go down the first floor."
    ),
    "house.bedroom": Room(
        "You are at your bedroom.\n"
        "You see a bed, a desk and a painting hanged on the wall.\n"
        "On the desk sits your laptop, a silver, premium Lenovo model.\n"
        "You can go out to the hallway."
    ),
    "house.bathroom": Room(
        "You are at the bathroom.\n"
        "A toilet and a shower stand close to each other.\n"
        "You can go out to the hallway"
    ),
    "house.balcony": Room(
        "You stand on the balcony.\n"
        "A coffee table and two chairs are turning to a nice view of the garden.\n"
        "You can enter back to the hallway."
    ),
    "house.attic": Room(
        "This is the attic. It is a small square space fulled with some interesting stuff.\n"
        "You can go down to the 2nd floor hallway."
    )
}
# Setting up room connections
rooms["outside"].compass.set(
    "in",
    rooms["house.livingRoom"],
    "You unlock the house front door and walk into the living room."
)
rooms["outside"].map.set(
    "house",
    rooms["house.livingRoom"],
    "You unlock the house front door and walk into the living room."
)
rooms["house.livingRoom"].map.set(
    "kitchen",
    rooms["house.kitchen"],
    "You enter the kitchen."
)
rooms["house.livingRoom"].map.set(
    "garden",
    rooms["house.garden"],
    "You open a light glass door which leads to the garden."
)
rooms["house.livingRoom"].map.set(
    "guest room",
    rooms["house.guestRoom"],
    "You open the door and step into the guest room."
)
rooms["house.livingRoom"].compass.set(
    "up",
    rooms["house.hallway"],
    "You climb the grand staircase and reach the hallway of the second floor."
)
rooms["house.livingRoom"].compass.set(
    "out",
    rooms["outside"],
    Chain(
        "You leave the house and close the door behind you.",
        Conditional(
            "flags.fbi",
            {
                "true": Chain(
                    "As soon as you open the front door you see a group armed men in black.\n"
                    "They wear bulletproof FBI suits, and each one of them is holding a gun.\n"
                    "You understand that hacking into the FBI wasn't the best idea ever.",
                    "$game.quit"
                )
            }
        )
    )
)
rooms["house.garden"].map.set(
    "house",
    rooms["house.livingRoom"],
    "You leave the garden and enter the living room."
)
rooms["house.garden"].compass.set(
    "in",
    rooms["house.livingRoom"],
    "You leave the garden and enter the living room."
)
rooms["house.guestRoom"].compass.set(
    "out",
    rooms["house.livingRoom"],
    "You leave the guest room and return to the living room."
)
rooms["house.kitchen"].compass.set(
    "out",
    rooms["house.livingRoom"],
    "You leave the kitchen and return to the living room."
)

rooms["house.hallway"].map.set(
    "bedroom",
    rooms["house.bedroom"],
    "You open your bedroom door and walk in."
)
rooms["house.hallway"].map.set(
    "bathroom",
    rooms["house.bathroom"],
    "You walk into the bathroom."
)
rooms["house.hallway"].map.set(
    "balcony",
    rooms["house.balcony"],
    "You step towards the end of the hallway and go out to the balcony."
)
rooms["house.hallway"].compass.set(
    "out",
    rooms["house.balcony"],
    "You step towards the end of the hallway and go out to the balcony."
)
rooms["house.hallway"].compass.set(
    "down",
    rooms["house.livingRoom"],
    "You climb down the staircase and step into the living room, reaching the ground floor."
)
rooms["house.hallway"].compass.set(
    "up",
    rooms["house.attic"],
    Lock(
        "rooms.attic.isLocked",
        "You climb to the attic through a sliding panel in the celling.",
        "The attic is currently locked!",
    )
)
rooms["house.bedroom"].compass.set(
    "out",
    rooms["house.hallway"],
    "You open the bedroom door and get out to the hallway."
)
rooms["house.bathroom"].compass.set(
    "out",
    rooms["house.hallway"],
    "You open the bathroom door and leave to the hallway."
)
rooms["house.balcony"].compass.set(
    "in",
    rooms["house.hallway"],
    ("You enter back into the house and find yourself in the hallway of the second floor.",
     "The warm sun starts to annoy you and you go back to the second floor hallway.")
)
rooms["house.balcony"].map.set(
    "house",
    rooms["house.hallway"],
    (
        "You enter back into the house and find yourself in the hallway of the second floor.",
        "The warm sun starts to annoy you and you go back to the second floor hallway."
    )
)
rooms["house.balcony"].compass.set(
    "down",
    rooms["house.garden"],
    "You decide to do something stupid and jump of the balcony.\n"
    "You find yourself in the garden, your body hurts like hell.",
    hidden=True
)
rooms["house.attic"].compass.set(
    "down",
    rooms["house.hallway"],
    "You open a panel in the floor and climb down to the 2nd floor hallway."
)
# Making interactives
inters = {
    "couch": Interactive(
        "couch",
        "This is a nice, comfy couch.",
        Conditional(
            "player.isSitting",
            {
                "true": "@inters.couch.getUp",
                "false": "@inters.couch.sit"
            }
        )
    ),
    "tv": Interactive(
        "tv",
        "This is a flat, OLED 4k 50\" television made by Samsung Ltd.",
        Menu(
            Chain(
                Conditional(
                    "inters.tv.on",
                    {
                        "true": "The TV is already on.",
                        "false": Manipulator(
                            {"inters.tv.on": True},
                            "You open the TV."
                        )
                    }
                ),
                "What will you watch?",
            ),
            {
                "Among Us channel": (
                    "You watch a show about the life of an imposter.\n"
                    "The show has a phenomenal deep meaning and it lasts 45 minutes before ending.",
                    "An excited announcer explains the changes and additions in the latest among us update.\n"
                    "Looks like you just wasted 15 minutes of your life.",
                    "'The ultimate guide to not being sus' shows up on screen.\n"
                    "You learn so much about how to not be sus!"
                ),
                "History channel": (
                    "You watch a fascinating documentary film about the rise of the internet.",
                    "You cry to the end of a dramatic movie on the very early beginning of WW2.",
                    "You watch a show about the secret meanings of the bible expressions."
                ),
                "Sports channel": Break(
                    Chain(
                        "You close TV immediately. Watching sports is boring!",
                        "@inters.tv.turnOff"
                    )

                ),
                "Turn TV off": Break("@inters.tv.turnOff")
            },
            True
        )
    ),
    "laptop": Interactive(
        "laptop",
        "This is a premium Lenovo model, with intel core i5 and a nice 15.4 inch display.",
        Chain(
            "You boot up the laptop and get it up and running.",
            Menu(
                "What do you want to do now?",
                {
                    "Go shopping on Ebay": "Ebay is currently down. Sorry!",
                    "Hack into the FBI {fillers.fbi}": Conditional(
                        "flags.fbi",
                        {
                            "false": Manipulator(
                                {"flags.fbi": True, "fillers.fbi": "'(again)'"},
                                "You spend several hours hacking into the FBI.\n"
                                "You do it! You download some data from their database to your computer.\n"
                                "You suddenly hear an aggressive knock on the house front door.\n"
                                "Wonder who it might be?",
                            ),
                            "true": "You hack into the FBI again, but this time you already know how to do it.\n"
                                    "It takes you much shorter period of time."
                        }
                    ),
                    "Turn laptop off": Break("You turn the laptop off.")
                },
                True,
            )
        )
    ),
    "trampoline": Interactive(
        "trampoline",
        "This is a trampoline. You can jump on it.",
        Chain(
            Manipulator({"inters.trampoline.rand": Random(1, 5)}),
            Conditional(
                "inters.trampoline.rand",
                {
                    "5": Teleporter(
                        rooms["house.balcony"],
                        "You jump so hard that you REACH THE BALCONY IN THE SECOND FLOOR!\n"
                        "You launch in the air and fall to the floor of the balcony.\n"
                    ),
                    "!5": "You jump on the trampoline long enough until you are satisfied. "
                }
            )
        )
    ),
    "painting": Interactive(
        "painting",
        "This is a painting of a fantasy dragon and a brave knight in an epic battle.",
        "Your slide the painting to the side, and reveal a small hole in the wall,"
        "approximately the size of a book.\n"
        "This is a safe place to store your killing tools. "
        "No one is supposed to find them here.\n"
    ),
    "bed": Interactive(
        "bed",
        "This is your bed. It is covered with among us bed sheet and blanket.",
        "You enter the bed and close your eyes.\n"
        "You lose your consciousness and find yourself in a dream.\n"
        "Unfortunately, this section of the game hasn't been written yet!"
    ),
    "lever": Interactive(
        "lever",
        "This lever can be used to lock/unlock the door leading to the attic.",
        Conditional(
            "rooms.attic.isLocked",
            {
                "true": Manipulator(
                    {"rooms.attic.isLocked": False},
                    "You pull the lever up and the panel to the attic opens."
                ),
                "false": Manipulator(
                    {"rooms.attic.isLocked": True},
                    "You pull the lever down and the panel to the attic closes."
                ),
            }
        )
    )
}
# Placing interactives
rooms["house.livingRoom"].interactives.add(inters["couch"], inters["tv"])
rooms["house.guestRoom"].interactives.add(inters["couch"])
rooms["house.bedroom"].interactives.add(inters["laptop"], inters["bed"], inters["painting"])
rooms["house.garden"].interactives.add(inters["trampoline"])
rooms["house.hallway"].interactives.add(inters["lever"])


# Adding custom events handler
def handler(event):
    if event == "game.quit":
        print("Game over!")
        exit(0)


def main():
    # Configuring the engine
    engine = Engine(handler, rooms["outside"])
    engine.events = events
    engine.flags = flags
    engine.start()


if __name__ == '__main__':
    main()
