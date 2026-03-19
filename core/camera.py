from settings import (
    CHUNK_SIZE,
    TILE_SIZE,
    WORLD_CHUNK_WIDTH,
    WORLD_CHUNK_HEIGHT,
)
from utils.maths import world_to_screen, screen_to_world


class Camera:
    def __init__(self):
        """Initialize the camera at the center of the world."""
        self.x = CHUNK_SIZE * TILE_SIZE * WORLD_CHUNK_WIDTH // 2
        self.y = CHUNK_SIZE * TILE_SIZE * WORLD_CHUNK_HEIGHT // 2

    def update(self, dx, dy):
        """Move the camera with wraparound world bounds."""
        self.x = int(dx + self.x) % (CHUNK_SIZE * TILE_SIZE * WORLD_CHUNK_WIDTH)
        self.y = int(dy + self.y) % (CHUNK_SIZE * TILE_SIZE * WORLD_CHUNK_HEIGHT)

    def world_to_screen(self, wx, wy):
        """Project a world-space point into screen-space."""
        return world_to_screen(wx, wy, self.x, self.y)

    def screen_to_world(self, sx, sy):
        """Project a screen-space point into world-space."""
        return screen_to_world(sx, sy, self.x, self.y)
