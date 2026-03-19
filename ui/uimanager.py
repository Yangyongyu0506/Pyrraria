from ui.ui_base import UIbase
from ui.healthbar import HealthBar
import pygame


class UIManager:
    def __init__(self, player):
        """Create and manage UI widgets."""
        self.health_bar = HealthBar(player)

    def update(self, dt: float):
        """Update UI widget states."""
        self.health_bar.update(dt)

    def render(self, surface: pygame.Surface):
        """Render UI widgets to the screen."""
        self.health_bar.render(surface)
