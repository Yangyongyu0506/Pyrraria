from ui.ui_base import UIbase
from ui.healthbar import HealthBar
import pygame

class UIManager:

    def __init__(self, player):
        self.health_bar = HealthBar(player)

    def update(self, dt: float):
        self.health_bar.update(dt)

    def render(self, surface: pygame.Surface):
        self.health_bar.render(surface)