"""Item registry for managing game items."""

from world.tools import MiningTool, Weapon

ITEMREG_TABLE = {
    1: {"name": "dirt", "color": (100, 50, 0, 255), "placeable": True},
    2: {"name": "stone", "color": (100, 100, 100, 255), "placeable": True},
    3: {"name": "grass", "color": (0, 200, 0, 255), "placeable": True},
    4: {"name": "ore", "color": (200, 200, 0, 255), "placeable": True},
    5: {"name": "sand", "color": (210, 190, 110, 255), "placeable": True},
    6: {"name": "water", "color": (40, 120, 220, 160), "placeable": False},
    7: {"name": "clay", "color": (150, 110, 90, 255), "placeable": True},
    8: {"name": "snow", "color": (230, 235, 240, 255), "placeable": True},
    9: {"name": "ice", "color": (170, 220, 255, 200), "placeable": True},
    10: {"name": "gravel", "color": (120, 120, 120, 255), "placeable": True},
    101: {
        "name": "basic_pickaxe",
        "color": (200, 180, 120, 255),
        "placeable": False,
        "stackable": False,
        "tool": MiningTool("basic_pickaxe", efficiency=1.0),
    },
    102: {
        "name": "basic_sword",
        "color": (180, 180, 190, 255),
        "placeable": False,
        "stackable": False,
        "tool": Weapon("basic_sword", efficiency=1.0),
    },
}
