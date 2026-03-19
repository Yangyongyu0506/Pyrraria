import pygame


class Hitbox:
    def __init__(self, offset_x, offset_y, width, height):
        """Axis-aligned hitbox relative to the owning entity."""
        self.x = offset_x  # relative to the entity's position
        self.y = offset_y
        self.width = width
        self.height = height

    def get_rect(self, entity_x, entity_y):
        """Return the world-space rectangle for this hitbox."""
        return pygame.Rect(
            entity_x + self.x, entity_y + self.y, self.width, self.height
        )
