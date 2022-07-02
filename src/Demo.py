from Core import Room, Interactive
from Events import Conditional, Manipulator
from Engine import Engine


def handler(event):
    print("Custom event fired: " + event)


bedroom = Room("This is a bedroom.")
bathroom = Room("This is a bathroom.")
couch = Interactive(
    "couch",
    "This is a nice, comfy couch.",
    Conditional(
        "player.isSitting",
        {
            "true": "@room.leave",
            "false": Manipulator(
                "You sit on the couch.",
                "player.isSitting",
                True
            )
        }
    )
)
bread = Interactive(
    "bread",
    "this is a bread. You can eat it.",
    Conditional(
        "bread.timesEaten",
        {
            "<6": Manipulator(
                "You eat from the bread",
                "bread.timesEaten",
                "+2"
            ),
            "6": "The bread is over!"
        }
    )
)


bedroom.compass.set("north", bathroom, "@room.leave")
bathroom.compass.set("south", bedroom, "@room.leave")
bedroom.map.set("bathroom", bathroom, "Hello")
bedroom.interactives.set("couch", couch)
bedroom.interactives.set("bread", bread)
engine = Engine(handler, bedroom)
engine.flags["player.isSitting"] = False
engine.flags["bread.timesEaten"] = 0
engine.events["room.leave"] = Conditional(
    "player.isSitting",
    {
        "true": Manipulator(
            "You get up from the couch.",
            "player.isSitting",
            False
        )
    }
)
engine.start()
