import pygame
import logging
from settings import FPS
from world.world import World
from core.camera import Camera
from core.input import InputManager
from entities.player import Player
from utils.maths import center_camera_on, screen_to_world
from entities.entitymanager import EntityManager
from ui.uimanager import UIManager


class Game:
    def __init__(self):
        logging.basicConfig(
            level=logging.WARNING, format="[%(asctime)s] %(levelname)s: %(message)s"
        )
        self.logger = logging.getLogger("pyrraria.game")
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Pyrraria")
        self.clock = pygame.time.Clock()
        self.running = True

        self.world = World(logger=self.logger)
        self.camera = Camera()

        self.input_manager = InputManager()
        self.entity_manager = EntityManager(self.world)
        spawn_x, spawn_y = self.world.spawn_x, self.world.spawn_y
        self.player = Player(spawn_x, spawn_y, self.world)
        self.entity_manager.add_entity(self.player)
        self.ui_manager = UIManager(self.player)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.process_input(dt)
            self.input_manager.update()
            self.update(dt)
            self.render()

        pygame.quit()

    def process_input(self, dt):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.on_exit()

    def update(self, dt):
        frame = self.input_manager.current_frame
        self.entity_manager.update(dt, frame)
        if 1 in frame.mouse_buttons_pressed:
            mx, my = frame.mouse_pos
            world_x, world_y = screen_to_world(mx, my, self.camera.x, self.camera.y)
            self.world.set_tile_at(world_x, world_y, 0)
        if self.player is not None:
            screen_w, screen_h = self.screen.get_size()
            self.camera.x, self.camera.y = center_camera_on(
                self.player.pos[0] + self.player.width / 2,
                self.player.pos[1] + self.player.height / 2,
                screen_w,
                screen_h,
            )
        self.world.update((self.camera.x, self.camera.y))
        self.ui_manager.update(dt)

    def render(self):
        self.world.render(self.screen, self.camera)
        self.entity_manager.render(self.screen, self.camera)
        self.ui_manager.render(self.screen)
        pygame.display.flip()

    def on_exit(self):
        self.logger.warning("Exiting game...")
        self.world.on_exit()
        self.entity_manager.on_exit()
        self.running = False
