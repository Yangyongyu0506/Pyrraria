import pygame
import logging
from settings import FPS
from world.world import World
from core.camera import Camera
from core.input import InputManager
from entities.player import Player
from utils.maths import center_camera_on
from entities.entitymanager import EntityManager
from ui.uimanager import UIManager
from systems.dig_system import DigSystem
from systems.pickup_system import PickupSystem
from systems.placement_system import PlacementSystem
from systems.discard_system import DiscardSystem
from systems.input_system import InputSystem
from systems.physics_system import PhysicsSystem


class Game:
    def __init__(self):
        """Initialize pygame, world state, and game subsystems."""
        logging.basicConfig(
            level=logging.WARNING, format="[%(asctime)s] %(levelname)s: %(message)s"
        )
        self.logger = logging.getLogger("pyrraria.game")
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN, vsync=1)
        pygame.display.set_caption("Pyrraria")
        self.clock = pygame.time.Clock()
        self.running = True

        self.world = World(logger=self.logger)
        self.camera = Camera()

        self.input_manager = InputManager()
        self.entity_manager = EntityManager(self.world)
        self.dig_system = DigSystem(self.world, self.entity_manager)
        self.pickup_system = PickupSystem(self.entity_manager)
        self.placement_system = PlacementSystem(self.world)
        self.discard_system = DiscardSystem(self.entity_manager)
        self.input_system = InputSystem(
            self.dig_system,
            self.pickup_system,
            self.placement_system,
            self.discard_system,
        )
        self.physics_system = PhysicsSystem()
        spawn_x, spawn_y = self.world.spawn_x, self.world.spawn_y
        self.player = Player(spawn_x, spawn_y, self.world, self.entity_manager)
        self.entity_manager.add_entity(self.player)
        self.ui_manager = UIManager(self.player, self.dig_system)

    def run(self):
        """Run the main game loop until shutdown."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.process_input(dt)
            self.input_manager.update()
            self.update(dt)
            self.render()
        pygame.quit()

    def process_input(self, dt):
        """Handle window-level events such as quitting."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.on_exit()

    def update(self, dt):
        """Advance game state by one frame."""
        frame = self.input_manager.current_frame
        self.input_system.update(self.player, frame, dt)
        self.entity_manager.update(dt, frame)
        self.physics_system.update(self.player, dt)
        if self.player is not None:
            screen_w, screen_h = self.screen.get_size()
            target_x, target_y = center_camera_on(
                self.player.pos[0] + self.player.width / 2,
                self.player.pos[1] + self.player.height / 2,
                screen_w,
                screen_h,
            )
            self.camera.update(target_x, target_y)
        self.world.update((self.camera.x, self.camera.y))
        self.ui_manager.update(dt)

    def render(self):
        """Draw world, entities, and UI to the screen."""
        self.world.render(self.screen, self.camera)
        self.entity_manager.render(self.screen, self.camera)
        self.ui_manager.render(self.screen)
        pygame.display.flip()

    def on_exit(self):
        """Cleanly shut down and persist world state."""
        self.logger.warning("Exiting game...")
        self.world.on_exit()
        self.player.on_exit()
        self.entity_manager.on_exit()
        self.running = False
