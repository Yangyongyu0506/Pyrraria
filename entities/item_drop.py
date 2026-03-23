import pygame

from entities.entity import Entity
from entities.hitbox import Hitbox
from settings import TILE_SIZE, PICKUP_LERP_SPEED
from world.tilereg import TILEREG_TABLE


class ItemDrop(Entity):
    def __init__(
        self,
        x: float,
        y: float,
        item_id: int,
        count: int = 1,
        lifespan: float = 10.0,
    ):
        """World item drop that can be picked up or auto-despawns."""
        super().__init__(x, y)
        self.item_id = item_id
        self.count = count
        self.lifespan = lifespan
        self.age = 0.0
        self.width = int(TILE_SIZE * 0.6)
        self.height = int(TILE_SIZE * 0.6)
        self.hitboxes.append(Hitbox(0, 0, self.width, self.height))
        self.is_noclip = True
        self.color = TILEREG_TABLE.get(item_id, {}).get("color", (220, 220, 220, 255))
        self.is_picking = False
        self.pick_target = None
        self.pick_speed = PICKUP_LERP_SPEED

    def update(self, _input_frame, dt: float):
        """Advance time and apply simple physics."""
        self.age += dt
        if self.age >= self.lifespan:
            self.is_alive = False
            return
        if self.is_picking and self.pick_target is not None:
            target_x, target_y = self.pick_target
            self.pos[0] += (target_x - self.pos[0]) * min(1.0, self.pick_speed * dt)
            self.pos[1] += (target_y - self.pos[1]) * min(1.0, self.pick_speed * dt)
        else:
            super().update_pos(dt)

    def start_pickup(self, target_x: float, target_y: float):
        """Begin lerping toward the pickup target."""
        self.is_picking = True
        self.pick_target = (target_x, target_y)

    def render(self, screen: pygame.Surface, camera):
        """Render the item drop as a small colored square."""
        screen_x = self.pos[0] - camera.x
        screen_y = self.pos[1] - camera.y
        pygame.draw.rect(
            screen,
            self.color,
            (int(screen_x), int(screen_y), self.width, self.height),
        )
