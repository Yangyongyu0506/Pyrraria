from entities.entity import Entity
from entities.hitbox import Hitbox
from entities.item_drop import ItemDrop
from ui.backpack import Backpack
from ui.inventory import Inventory
from core.input import InputFrame
from world.world import World
from utils.maths import world_to_screen, lerp, screen_to_world
from settings import DIG_BASE_TIME, PICKUP_RADIUS, TILE_SIZE
from world.tilereg import TILE_DROPS
from world.tilereg import TILEREG_TABLE
from entities.itemreg import ITEMREG_TABLE
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
        self.backpack = Backpack()

        if self.inventory.is_empty():
            self.inventory.add_item(101, 1)
            self.inventory.add_item(102, 1)
            self.inventory.select_slot(0)

        self.dig_target = None
        self.dig_timer = 0.0
        self.dig_required = 0.0

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
        if pygame.K_e in input_frame.keys_pressed:
            self.backpack.toggle()

        if self.backpack.is_open:
            if pygame.K_h in input_frame.keys_pressed:
                self.backpack.move_cursor(-1, 0)
            if pygame.K_l in input_frame.keys_pressed:
                self.backpack.move_cursor(1, 0)
            if pygame.K_k in input_frame.keys_pressed:
                self.backpack.move_cursor(0, -1)
            if pygame.K_j in input_frame.keys_pressed:
                self.backpack.move_cursor(0, 1)

            if pygame.K_1 in input_frame.keys_pressed:
                self.backpack.swap_with_inventory(self.inventory, 0)
            if pygame.K_2 in input_frame.keys_pressed:
                self.backpack.swap_with_inventory(self.inventory, 1)
            if pygame.K_3 in input_frame.keys_pressed:
                self.backpack.swap_with_inventory(self.inventory, 2)
            if pygame.K_4 in input_frame.keys_pressed:
                self.backpack.swap_with_inventory(self.inventory, 3)
            if pygame.K_5 in input_frame.keys_pressed:
                self.backpack.swap_with_inventory(self.inventory, 4)
            if pygame.K_6 in input_frame.keys_pressed:
                self.backpack.swap_with_inventory(self.inventory, 5)
            if pygame.K_7 in input_frame.keys_pressed:
                self.backpack.swap_with_inventory(self.inventory, 6)
            if pygame.K_8 in input_frame.keys_pressed:
                self.backpack.swap_with_inventory(self.inventory, 7)
            if pygame.K_9 in input_frame.keys_pressed:
                self.backpack.swap_with_inventory(self.inventory, 8)

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

        if not self.backpack.is_open:
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

        if 1 in input_frame.mouse_buttons_held and not self.backpack.is_open:
            selected = self.inventory.get_selected()
            item_def = ITEMREG_TABLE.get(selected.item_id, {}) if selected else {}
            tool = item_def.get("tool") if selected else None
            if tool is None or not tool.can_dig:
                self.reset_dig()
            else:
                mx, my = input_frame.mouse_pos
                world_x, world_y = screen_to_world(
                    mx, my, self.world.camx, self.world.camy
                )
                if (
                    math.hypot(world_x - self.pos[0], world_y - self.pos[1])
                    > PICKUP_RADIUS
                ):
                    self.reset_dig()
                else:
                    tile_id = self.world.get_tile_at(world_x, world_y)
                    if tile_id is None or tile_id == 0:
                        self.reset_dig()
                    else:
                        tile_x = (world_x // TILE_SIZE) * TILE_SIZE
                        tile_y = (world_y // TILE_SIZE) * TILE_SIZE
                        target = (tile_x, tile_y)
                        if target != self.dig_target:
                            self.dig_target = target
                            self.dig_timer = 0.0
                            hardness = TILEREG_TABLE[tile_id]["hardness"]
                            self.dig_required = tool.dig_time(hardness, DIG_BASE_TIME)
                        self.dig_timer += dt
                        if self.dig_timer >= self.dig_required:
                            self.break_tile(tile_x, tile_y, tile_id)
                            self.reset_dig()
        if 1 in input_frame.mouse_buttons_released:
            self.reset_dig()
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
                if (
                    math.hypot(world_x - self.pos[0], world_y - self.pos[1])
                    <= PICKUP_RADIUS
                ):
                    if self.world.get_tile_at(world_x, world_y) == 0:
                        self.world.set_tile_at(world_x, world_y, selected.item_id)
                        self.inventory.remove_selected(1)

        super().update_pos(dt)

    def break_tile(self, tile_x: float, tile_y: float, tile_id: int):
        """Remove a tile and spawn a drop."""
        drop_id = TILE_DROPS.get(tile_id)
        if drop_id is not None:
            if self.entity_manager is not None:
                drop = ItemDrop(tile_x, tile_y, drop_id, 1)
                self.entity_manager.add_entity(drop)
            else:
                self.inventory.add_item(drop_id, 1)
        self.world.set_tile_at(tile_x, tile_y, 0)

    def reset_dig(self):
        """Clear digging state."""
        self.dig_target = None
        self.dig_timer = 0.0
        self.dig_required = 0.0

    def dig_progress(self) -> tuple[tuple[float, float] | None, float]:
        """Return dig target and progress ratio (0.0-1.0)."""
        if self.dig_target is None or self.dig_required <= 0:
            return None, 0.0
        return self.dig_target, min(1.0, self.dig_timer / self.dig_required)

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
