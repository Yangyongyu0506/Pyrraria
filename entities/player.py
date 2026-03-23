from entities.entity import Entity
from entities.hitbox import Hitbox
from entities.item_drop import ItemDrop
from ui.inventory import Inventory
from core.input import InputFrame
from world.world import World
from utils.maths import world_to_screen, lerp, screen_to_world
from settings import PICKUP_RADIUS, TILE_SIZE
from world.tilereg import TILE_DROPS
from world.itemreg import ITEMREG_TABLE
import pygame
import math
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
        self.max_fall_speed = 420.0

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
        moving_left = pygame.K_a in input_frame.keys_held
        moving_right = pygame.K_d in input_frame.keys_held
        on_ground = self.is_on_ground()
        if moving_left and not moving_right:
            self.vel[0] = -self.move_speed
        elif moving_right and not moving_left:
            self.vel[0] = self.move_speed
        else:
            friction = self.ground_friction if on_ground else self.air_friction
            self.vel[0] -= self.vel[0] * min(1.0, friction * dt)

        jump_pressed = (
            pygame.K_SPACE in input_frame.keys_pressed
            or pygame.K_w in input_frame.keys_pressed
        )
        if jump_pressed and self.is_on_ground():
            self.vel[1] = -self.jump_speed

        if self.vel[1] > self.max_fall_speed:
            self.vel[1] = self.max_fall_speed

        # Update invincibility state
        if self.is_hurt:
            self.invincibility_tick += dt
            self.update_font()
            if self.invincibility_tick >= self.invincibility_interval:
                self.is_hurt = False
                self.invincibility_tick = 0.0
                self.reset_font()

        if pygame.K_1 in input_frame.keys_pressed:
            self.inventory.select_slot(0)
        if pygame.K_2 in input_frame.keys_pressed:
            self.inventory.select_slot(1)
        if pygame.K_3 in input_frame.keys_pressed:
            self.inventory.select_slot(2)
        if pygame.K_4 in input_frame.keys_pressed:
            self.inventory.select_slot(3)
        if pygame.K_5 in input_frame.keys_pressed:
            self.inventory.select_slot(4)
        if pygame.K_6 in input_frame.keys_pressed:
            self.inventory.select_slot(5)
        if pygame.K_7 in input_frame.keys_pressed:
            self.inventory.select_slot(6)
        if pygame.K_8 in input_frame.keys_pressed:
            self.inventory.select_slot(7)
        if pygame.K_9 in input_frame.keys_pressed:
            self.inventory.select_slot(8)

        if 1 in input_frame.mouse_buttons_pressed:
            mx, my = input_frame.mouse_pos
            world_x, world_y = screen_to_world(mx, my, self.world.camx, self.world.camy)
            if math.hypot(world_x - self.pos[0], world_y - self.pos[1]) <= PICKUP_RADIUS:
                tile_id = self.world.get_tile_at(world_x, world_y)
                if tile_id is not None and tile_id != 0:
                    drop_id = TILE_DROPS.get(tile_id)
                    if drop_id is not None:
                        if self.entity_manager is not None:
                            tile_x = (world_x // TILE_SIZE) * TILE_SIZE
                            tile_y = (world_y // TILE_SIZE) * TILE_SIZE
                            drop = ItemDrop(tile_x, tile_y, drop_id, 1)
                            self.entity_manager.add_entity(drop)
                        else:
                            self.inventory.add_item(drop_id, 1)
                    self.world.set_tile_at(world_x, world_y, 0)
        if 3 in input_frame.mouse_buttons_pressed:
            selected = self.inventory.get_selected()
            if (
                selected is not None
                and selected.count > 0
                and ITEMREG_TABLE[selected.item_id]["placeable"]
            ):
                mx, my = input_frame.mouse_pos
                world_x, world_y = screen_to_world(
                    mx, my, self.world.camx, self.world.camy
                )
                if math.hypot(world_x - self.pos[0], world_y - self.pos[1]) <= PICKUP_RADIUS:
                    if self.world.get_tile_at(world_x, world_y) == 0:
                        self.world.set_tile_at(world_x, world_y, selected.item_id)
                        self.inventory.remove_selected(1)

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
