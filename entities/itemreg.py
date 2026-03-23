"""Item registry for managing game items."""
import pygame
from settings import DIR_ROOT, SLOT_SIZE
from world.tools import MiningTool, Weapon

def load_img(item_id):
    """Load an item image, returning None on failure."""
    try:
        img = pygame.image.load(f"{DIR_ROOT}/assets/items/{item_id}.png")
        return pygame.transform.scale(img, (SLOT_SIZE, SLOT_SIZE))
    except FileNotFoundError:
        return None

ITEMREG_TABLE = {
    1: {"name": "dirt", "color": (100, 50, 0, 255), "placeable": True, "surf": load_img(1)},
    2: {"name": "stone", "color": (100, 100, 100, 255), "placeable": True, "surf": load_img(2)},
    3: {"name": "grass", "color": (0, 200, 0, 255), "placeable": True, "surf": load_img(3)},
    4: {"name": "ore", "color": (200, 200, 0, 255), "placeable": True, "surf": load_img(4)},
    5: {"name": "sand", "color": (210, 190, 110, 255), "placeable": True, "surf": load_img(5)},
    6: {"name": "water", "color": (40, 120, 220, 160), "placeable": False, "surf": load_img(6)},
    7: {"name": "clay", "color": (150, 110, 90, 255), "placeable": True, "surf": load_img(7)},
    8: {"name": "snow", "color": (230, 235, 240, 255), "placeable": True, "surf": load_img(8)},
    9: {"name": "ice", "color": (170, 220, 255, 200), "placeable": True, "surf": load_img(9)},
    10: {"name": "gravel", "color": (120, 120, 120, 255), "placeable": True, "surf": load_img(10)},
    101: {
        "name": "basic_pickaxe",
        "color": (200, 180, 120, 255),
        "placeable": False,
        "stackable": False,
        "tool": MiningTool("basic_pickaxe", efficiency=1.0),
        "surf": load_img(101),
    },
    102: {
        "name": "basic_sword",
        "color": (180, 180, 190, 255),
        "placeable": False,
        "stackable": False,
        "tool": Weapon("basic_sword", efficiency=1.0),
        "surf": load_img(102),
    },
}
