from Core import Room, Interactive
from Events import Conditional, Manipulator, Chain, Menu, Break, Teleporter, Random
from Engine import Engine


# Custom event handler
def handler(event):
    if event == "game.quit":
        engine.print("Game over!")
        exit(0)


prompts = {
    "house.outside-house": "You unlock the house front door and walk into the living room.",
    "house.garden-house": "You leave the garden and enter the living room.",
    "house.hallway-balcony": "You step towards the end of the hallway and go out to the balcony.",
    "house.downstairs": "You climb down the staircase and step into the living room, reaching the ground floor.",
    "house.balcony-hallway": (
        "You enter back into the house and find yourself in the hallway of the second floor.",
        "The warm sun starts to annoy you and you go back to the second floor hallway."
    ),
    "house.balcony-garden": "You decide to be stupid and jump of the balcony.\n"
                            "You fall to the garden and hit the hard ground.\n"
                            "You think you heard one of your bones breaking."
}

# Defining rooms
# 1st floor
outside = Room(
    "You stand outside your house.\n"
    "What are you waiting for? Enter the house."
)
living_room = Room(
    "You are at the house living room. \n" 
    "A couch stands in front of a coffee table and a 50 inch television.\n" 
    "You can enter the kitchen, the guest room and the garden.\n" 
    "You can also take the stairs and go up to the second floor, "
    "or leave the house and go out.",
    leave="@room.leave"
)
garden = Room(
    "The garden is breathtaking, with green grass and flowers all around.\n"
    "A huge trampoline is in the center of the garden, waiting to be jumped on.\n"
    "You can enter back into the house."
)
kitchen = Room(
    "The kitchen is accessorized with a fridge, "
    "oven with stove and a sink with some dirty dishes.\n"
    "There is also a dining table you can eat on.\n"
    "You can go out to the living room."
)
guest_room = Room(
    "This is a usual guest room - with a couch, a bed and a mini bar.\n"
    "When you have guests overnight they stay here.\n"
    "You can go out to the living room.",
    leave="@room.leave"
)

# 2nd floor
hallway = Room(
    "You are at the hallway of the house second floor.\n"
    "You can enter the bedroom, bathroom and balcony, "
    "or take the stairs and go down the first floor."
)
bedroom = Room(
    "You are at your bedroom.\n"
    "You see a bed, a desk and a painting hanged on the wall.\n"
    "On the desk sits your laptop, a silver, premium Lenovo model.\n"
    "You can go out to the hallway."
)
bathroom = Room(
    "You are at the bathroom.\n"
    "A toilet and a shower stand close to each other.\n"
    "You can go out to the hallway"
)
balcony = Room(
    "You stand on the balcony.\n"
    "A coffee table and two chairs are turning to a nice view of the garden.\n"
    "You can enter back to the hallway."
)

# Set up room connections
outside.compass.set("in", living_room, prompts["house.outside-house"])
outside.map.set("house", living_room, prompts["house.outside-house"])
living_room.map.set("kitchen", kitchen, "You enter the kitchen.")
living_room.map.set("garden", garden, "You open a light glass door which leads to the garden.")
living_room.map.set("guest room", guest_room, "You open the door and step into the guest room.")
living_room.compass.set("up", hallway, "You climb the grand staircase and reach the hallway of the second floor.")
living_room.compass.set(
    "out",
    outside,
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
garden.map.set("house", living_room, prompts["house.garden-house"])
garden.compass.set("in", living_room, prompts["house.garden-house"])
hallway.map.set("bedroom", bedroom, "You open your bedroom door and walk in.")
hallway.map.set("bathroom", bathroom, "You walk into the bathroom.")
hallway.map.set("balcony", balcony, prompts["house.hallway-balcony"])
hallway.compass.set("out", balcony, prompts["house.hallway-balcony"])
hallway.compass.set("down", living_room, prompts["house.downstairs"])
bedroom.compass.set("out", hallway, "You open the bedroom door and get out to the hallway.")
bathroom.compass.set("out", hallway, "You open the bathroom door and leave to the hallway.")
guest_room.compass.set("out", living_room, "You leave the guest room and return to the living room.")
kitchen.map.set("out", living_room, "You leave the kitchen and return to the living room.")
balcony.compass.set("in", hallway, prompts["house.balcony-hallway"])
balcony.map.set("house", hallway, prompts["house.balcony-hallway"])
balcony.compass.set("down", garden, prompts["house.balcony-garden"], hidden=True)


# Defining interactives
couch = Interactive(
    "couch",
    "This is a nice, comfy couch.",
    Conditional(
        "player.isSitting",
        {
            "true": "@inters.couch.getUp",
            "false": "@inters.couch.sit"
        }
    )
)
guest_couch = Interactive(
    "couch",
    "This is the guest couch. The sofa in the living room is much better!",
    Conditional(
        "player.isSitting",
        {
            "true": "@inters.couch.getUp",
            "false": "@inters.couch.sit"
        }
    )
)
tv = Interactive(
    "tv",
    "This is a flat, OLED 4k 50\" television made by Samsung Ltd.",
    Menu(
        Chain(
            Conditional(
                "inters.tv.isWorking",
                {
                    "true": "The TV is already on.",
                    "false": Manipulator(
                        {"inters.tv.isWorking": True},
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
)
laptop = Interactive(
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
)
trampoline = Interactive(
    "trampoline",
    "This is a trampoline. You can jump on it.",
    Chain(
        Manipulator({"inters.trampoline.rand": Random(1, 5)}),
        Conditional(
            "inters.trampoline.rand",
            {
                "5": Teleporter(
                    balcony,
                    "You jump so hard that you REACH THE BALCONY IN THE SECOND FLOOR!\n"
                    "You launch in the air and fall to the floor of the balcony.\n"
                ),
                "!5": "You jump on the trampoline long enough until you are satisfied. "
            }
        )
    )
)
painting = Interactive(
    "painting",
    "This is a painting of a fantasy dragon and a brave knight in an epic battle.",
    "Your slide the painting to the side, and reveal a small hole in the wall,"
    "approximately the size of a book.\n"
    "This is a safe place to store your killing tools. "
    "No one is supposed to find them here.\n"
)
bed = Interactive(
    "bed",
    "This is your bed. It is covered with among us bed sheet and blanket.",
    "You enter the bed and close your eyes.\n"
    "You lose your consciousness and find yourself in a dream.\n"
    "Unfortunately, this section of the game hasn't been written yet!"
)

# Placing interactives
living_room.interactives.add(couch, tv)
guest_room.interactives.add(guest_couch)
bedroom.interactives.add(laptop, bed, painting)
garden.interactives.add(trampoline)

flags = {
    "player.isSitting": False,
    "inters.tv.isWorking": False,
    "inters.trampoline.rand": 0,
    "flags.fbi": False,
    "fillers.fbi": "",
}

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
    "inters.tv.turnOff": Manipulator({"inters.tv.isWorking": False})
}

# Setting engine
engine = Engine(handler, outside)
engine.events = events
engine.flags = flags
engine.start()
