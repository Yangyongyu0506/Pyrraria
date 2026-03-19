import pygame
from ui.ui_base import UIbase
from entities.player import Player
from settings import HEALTH_BAR_SIZE, HEALTH_BAR_POS


class HealthBar(UIbase):
    def __init__(
        self,
        player: Player,
        pos: tuple[int, int] = HEALTH_BAR_POS,
        size: tuple[int, int] = HEALTH_BAR_SIZE,
    ):
        """Initialize a health bar bound to a player."""
        super().__init__()
        self.player = player
        self.pos = pos
        self.size = size
        self.max_health = player.max_health
        self.is_shown = True  # Health bar is always shown for now

    def update(self, dt: float):
        """No-op: the bar reads player state directly."""
        pass  # Health bar updates based on player's health, so no need to do anything here

    def render(self, surface: pygame.Surface):
        """Draw the health bar to the screen."""
        if not self.is_shown:
            return
        health_ratio = self.player.health / self.max_health
        health_bar_width = int(self.size[0] * health_ratio)
        health_bar_rect = pygame.Rect(
            self.pos[0], self.pos[1], health_bar_width, self.size[1]
        )
        if health_ratio > 0.3:
            pygame.draw.rect(surface, (0, 255, 0), health_bar_rect)  # Green for health
        else:
            pygame.draw.rect(
                surface, (255, 0, 0), health_bar_rect
            )  # Red for low health
        # Draw border
        border_rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        pygame.draw.rect(
            surface, (255, 255, 255), border_rect, 2
        )  # White border with thickness 2
