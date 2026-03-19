import numpy as np
import pygame
from core.camera import Camera
from entities.hitbox import Hitbox
from settings import ACC_G
from utils.maths import world_to_screen


class Entity:
    def __init__(self, x: float, y: float):
        self.pos = np.array([x, y], dtype=float)
        self.prev_pos = np.array([x, y], dtype=float)
        self.vel = np.array([0.0, 0.0])
        self.last_vel = np.array([0.0, 0.0])
        self.max_vel = np.array([300, 300])
        self.acc = np.array([0.0, ACC_G])
        self.is_noclip: bool = False
        self.hitboxes: list[Hitbox] = []
        self.is_alive: bool = True
        self.did_land = False
        self.landed_speed = 0.0

    def update_pos(self, dt):
        if self.is_alive:
            self.prev_pos = self.pos.copy()
            self.last_vel = self.vel.copy()
            self.vel += self.acc * dt
            # self.vel = np.clip(self.vel, -self.max_vel, self.max_vel)
            self.pos += self.vel * dt

    def set_max_vel(self, max_vx, max_vy):
        self.max_vel[:] = [max_vx, max_vy]

    def set_pos(self, x, y):
        self.pos[:] = [x, y]

    def set_vel(self, vx, vy):
        # Avoids creating a new array
        self.vel[:] = [vx, vy]

    def set_acc(self, ax, ay):
        self.acc[:] = [ax, ay]

    def on_dead(self):
        # Placeholder for death logic, e.g. dropping items, playing animation, etc.
        self.is_alive = False
        pass

    def render(self, screen: pygame.Surface, camera: Camera):
        # Placeholder: render as a red circle
        # Mind that camera's position is the left-top corner of the screen, while entity's position is in world coordinates
        screen_x, screen_y = world_to_screen(
            self.pos[0], self.pos[1], camera.x, camera.y
        )
        pygame.draw.circle(screen, (255, 0, 0, 128), (int(screen_x), int(screen_y)), 10)
