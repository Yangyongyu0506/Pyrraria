from entities.entity import Entity
from entities.hitbox import Hitbox
from core.input import InputFrame
from world.world import World
from utils.maths import world_to_screen
from settings import TILE_SIZE
import pygame


class Player(Entity):
    def __init__(
        self,
        x: int,
        y: int,
        world: World,
        width: int = TILE_SIZE,
        height: int = 2 * TILE_SIZE,
    ):
        """Create a player entity with movement and health state."""
        super().__init__(x, y)
        self.world = world
        self.width = width
        self.height = height
        self.hitboxes.append(Hitbox(0, 0, width, height))
        self.move_speed = 120
        self.jump_speed = 180

        # health logics
        self.max_health = 100
        self.health = self.max_health
        self.invincibility_tick = 0.0
        self.invincibility_interval = 0.1
        self.is_hurt = False
        self.fall_damage_threshold = 180.0
        self.fall_damage_scale = 0.08

    def is_on_ground(self) -> bool:
        """Return True if any hitbox touches solid ground below."""
        for hitbox in self.hitboxes:
            rect = hitbox.get_rect(self.pos[0], self.pos[1])
            ground_rect = pygame.Rect(rect.left, rect.bottom, rect.width, 1)
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
        self.health -= damage
        self.is_hurt = True
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            self.on_dead()

    def update(self, input_frame: InputFrame, dt: float):
        """Handle input, update movement intent, and integrate motion."""
        if pygame.K_a in input_frame.keys_held:
            self.vel[0] = -self.move_speed
        elif pygame.K_d in input_frame.keys_held:
            self.vel[0] = self.move_speed
        else:
            self.vel[0] = 0

        jump_pressed = (
            pygame.K_SPACE in input_frame.keys_pressed
            or pygame.K_w in input_frame.keys_pressed
        )
        if jump_pressed and self.is_on_ground():
            self.vel[1] = -self.jump_speed

        # Update invincibility state
        if self.is_hurt:
            self.invincibility_tick += dt
            if self.invincibility_tick >= self.invincibility_interval:
                self.is_hurt = False
                self.invincibility_tick = 0.0

        super().update_pos(dt)

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
                (255, 0, 0, 10),
                (int(screen_x), int(screen_y), self.width, self.height),
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
