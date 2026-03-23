from ui.health import HealthBar
from entities.player import Player
import pygame


class UIManager:
    def __init__(self, player: Player):
        """Create and manage UI widgets."""
        self.health_bar = HealthBar(player)
        self.player = player

    def update(self, dt: float):
        """Update UI widget states."""
        self.health_bar.update(dt)

    def render(self, surface: pygame.Surface):
        """Render UI widgets to the screen."""
        self.health_bar.render(surface)
        self.player.inventory.render(surface)
        self.player.backpack.render(surface)
