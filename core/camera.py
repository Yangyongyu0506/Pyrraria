from settings import CHUNK_PX, WORLD_W_PX, WORLD_H_PX
from utils.maths import world_to_screen, screen_to_world, lerp


class Camera:
    def __init__(self):
        """Initialize the camera at the center of the world."""
        self.x = WORLD_W_PX // 2
        self.y = WORLD_H_PX // 2
        self.lerp = 0.15

    def update(self, x, y):
        """Set the camera position with wraparound world bounds."""
        self.x = lerp(self.x, x, self.lerp)
        self.y = lerp(self.y, y, self.lerp)
        self.x = int(self.x) % WORLD_W_PX
        self.y = int(self.y) % WORLD_H_PX

    def world_to_screen(self, wx, wy):
        """Project a world-space point into screen-space."""
        return world_to_screen(wx, wy, self.x, self.y)

    def screen_to_world(self, sx, sy):
        """Project a screen-space point into world-space."""
        return screen_to_world(sx, sy, self.x, self.y)
