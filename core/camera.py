from settings import (
    CHUNK_SIZE,
    TILE_SIZE,
    WORLD_CHUNK_WIDTH,
    WORLD_CHUNK_HEIGHT,
)
from utils.maths import world_to_screen, screen_to_world


class Camera:
    def __init__(self):
        self.x = CHUNK_SIZE * TILE_SIZE * WORLD_CHUNK_WIDTH // 2
        self.y = CHUNK_SIZE * TILE_SIZE * WORLD_CHUNK_HEIGHT // 2

    def update(self, dx, dy):
        self.x = int(dx + self.x) % (CHUNK_SIZE * TILE_SIZE * WORLD_CHUNK_WIDTH)
        self.y = int(dy + self.y) % (CHUNK_SIZE * TILE_SIZE * WORLD_CHUNK_HEIGHT)

    def world_to_screen(self, wx, wy):
        return world_to_screen(wx, wy, self.x, self.y)

    def screen_to_world(self, sx, sy):
        return screen_to_world(sx, sy, self.x, self.y)
