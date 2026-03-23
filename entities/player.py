from entities.entity import Entity
from entities.hitbox import Hitbox
from ui.backpack import Backpack
from ui.inventory import Inventory
from core.input import InputFrame
from world.world import World
from utils.maths import world_to_screen, lerp, screen_to_world
from settings import TILE_SIZE
import pygame
import numpy as np


class Player(Entity):
    def __init__(
        self,
        x: int,
        y: int,
        world: World,
        entity_manager=None,
        width: int = TILE_SIZE,
        height: int = 2 * TILE_SIZE,
    ):
        """Create a player entity with movement and health state."""
        super().__init__(x, y)
        self.world = world
        self.entity_manager = entity_manager
        self.width = width
        self.height = height
        self.hitboxes.append(Hitbox(0, 0, width, height))
        self.move_speed = 140
        self.jump_speed = 180
        self.ground_friction = 12.0
        self.air_friction = 2.5
        self.max_fall_speed = 1000.0

        # health logics
        self.max_health = 100
        self.health = self.max_health
        self.last_health = self.health
        self.invincibility_tick = 0.0
        self.invincibility_interval = 0.6
        self.is_hurt = False
        self.fall_damage_threshold = 180.0
        self.fall_damage_scale = 0.08

        # inventory
        self.inventory = Inventory()
        self.backpack = Backpack()

        if self.inventory.is_empty():
            self.inventory.add_item(101, 1)
            self.inventory.add_item(102, 1)
            self.inventory.select_slot(0)

        # fonts
        self.font = pygame.font.SysFont(None, 24)
        self.font_pos = (width // 2, height // 2)
        self.target_font_pos = self.font_pos

    def reset_font(self):
        """Reset the font to default settings."""
        self.font_pos = (self.width // 2, self.height // 2)

    def update_font(self):
        """Move the font position towards the target for a simple animation."""
        self.font_pos = (
            int(lerp(self.font_pos[0], self.target_font_pos[0], 0.2)),
            int(lerp(self.font_pos[1], self.target_font_pos[1], 0.2)),
        )

    def refresh_font(self):
        self.target_font_pos = (
            self.width // 2 + np.random.randint(-30, 30),
            self.height // 2 + np.random.randint(-30, 30),
        )

    def is_on_ground(self) -> bool:
        """Return True if any hitbox touches solid ground below."""
        for hitbox in self.hitboxes:
            rect = hitbox.get_rect(self.pos[0], self.pos[1])
            ground_rect = pygame.Rect(rect.left, rect.bottom, rect.width, 2)
            if self.world.is_rect_solid(ground_rect):
                return True
        return False

    def solve_damage(self, landed_speed: float):
        """Apply fall damage based on landing speed."""
        if landed_speed <= self.fall_damage_threshold:
            return
        damage = int(
            (landed_speed - self.fall_damage_threshold) * self.fall_damage_scale
        )
        if damage > 0:
            self.on_hurt(damage)

    def on_hurt(self, damage: int):
        """Apply damage and trigger death if health reaches zero."""
        if self.is_hurt:
            return
        self.last_health = self.health
        self.health -= damage
        self.is_hurt = True
        self.refresh_font()
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            self.on_dead()

    def update(self, input_frame: InputFrame, dt: float):
        """Handle input, update movement intent, and integrate motion."""
        # Update invincibility state
        if self.is_hurt:
            self.invincibility_tick += dt
            self.update_font()
            if self.invincibility_tick >= self.invincibility_interval:
                self.is_hurt = False
                self.invincibility_tick = 0.0
                self.reset_font()

        super().update_pos(dt)

    def screen_to_world(self, sx: float, sy: float):
        """Convert screen coordinates to world coordinates."""
        return screen_to_world(sx, sy, self.world.camx, self.world.camy)

    def post_update(self, dt: float):
        """Apply post-collision effects such as landing damage."""
        if self.did_land:
            self.solve_damage(self.landed_speed)

    def render(self, screen: pygame.Surface, camera):
        """Render the player with a simple colored rectangle."""
        screen_x, screen_y = world_to_screen(
            self.pos[0], self.pos[1], camera.x, camera.y
        )
        if self.is_hurt:
            pygame.draw.rect(
                screen,
                (100, 0, 0, 10),
                (int(screen_x), int(screen_y), self.width, self.height),
            )
            font_surf = self.font.render(
                f"-{self.last_health - self.health}", True, (255, 0, 0)
            )
            screen.blit(
                font_surf,
                (int(screen_x + self.font_pos[0]), int(screen_y + self.font_pos[1])),
            )
        else:
            pygame.draw.rect(
                screen,
                (0, 255, 0, 10),
                (int(screen_x), int(screen_y), self.width, self.height),
            )

    def on_dead(self):
        """Respawn the player at the world spawn point."""
        super().on_dead()
        self.pos[:] = [self.world.spawn_x, self.world.spawn_y]
        self.is_alive = True
        self.health = 50

    def on_exit(self):
        """Persist player state such as inventory on game exit."""
        self.inventory.on_exit()
        self.backpack.on_exit()
