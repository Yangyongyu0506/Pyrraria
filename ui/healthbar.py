import pygame
from ui.ui_base import UIbase
from entities.player import Player


class HealthBar(UIbase):
    def __init__(
        self,
        player: Player,
        pos: tuple[int, int] = (10, 10),
        size: tuple[int, int] = (100, 10),
    ):
        super().__init__()
        self.player = player
        self.pos = pos
        self.size = size
        self.max_health = player.max_health

    def update(self, dt: float):
        pass  # Health bar updates based on player's health, so no need to do anything here

    def render(self, surface: pygame.Surface):
        health_ratio = self.player.health / self.max_health
        health_bar_width = int(self.size[0] * health_ratio)
        health_bar_rect = pygame.Rect(
            self.pos[0], self.pos[1], health_bar_width, self.size[1]
        )
        pygame.draw.rect(surface, (255, 0, 0), health_bar_rect)  # Red for health
        # Draw border
        border_rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        pygame.draw.rect(
            surface, (255, 255, 255), border_rect, 2
        )  # White border with thickness 2
