"""Tile registry mapping IDs to render and physics properties."""
import pygame

from settings import DIR_ROOT, TILE_SIZE

def load_img(tile_id):
    """Load a tile image, returning None on failure."""
    try:
        img = pygame.image.load(f"{DIR_ROOT}/assets/tiles/{tile_id}.png")
        return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    except FileNotFoundError:
        return None


TILEREG_TABLE = {
    0: {"name": "air", "color": (0, 0, 0, 0), "solid": False, "hardness": 0, "surf": load_img(0)},
    1: {"name": "dirt", "color": (100, 50, 0, 255), "solid": True, "hardness": 1, "surf": load_img(1)},
    2: {"name": "stone", "color": (100, 100, 100, 255), "solid": True, "hardness": 3, "surf": load_img(2)},
    3: {"name": "grass", "color": (0, 200, 0, 255), "solid": True, "hardness": 1, "surf": load_img(3)},
    4: {"name": "ore", "color": (200, 200, 0, 255), "solid": True, "hardness": 4, "surf": load_img(4)},
    5: {"name": "sand", "color": (210, 190, 110, 255), "solid": True, "hardness": 1, "surf": load_img(5)},
    6: {"name": "water", "color": (40, 120, 220, 160), "solid": False, "hardness": 0, "surf": load_img(6)},
    7: {"name": "clay", "color": (150, 110, 90, 255), "solid": True, "hardness": 2, "surf": load_img(7)},
    8: {"name": "snow", "color": (230, 235, 240, 255), "solid": True, "hardness": 1, "surf": load_img(8)},
    9: {"name": "ice", "color": (170, 220, 255, 200), "solid": True, "hardness": 2, "surf": load_img(9)},
    10: {"name": "gravel", "color": (120, 120, 120, 255), "solid": True, "hardness": 2, "surf": load_img(10)},
}

TILE_DROPS = {
    1: 1,  # dirt
    2: 2,  # stone
    3: 3,  # grass
    4: 4,  # ore
    5: 5,  # sand
    6: 6,  # water
    7: 7,  # clay
    8: 8,  # snow
    9: 9,  # ice
    10: 10,  # gravel
}
