from ui.ui_base import UIbase
from ui.healthbar import HealthBar
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
        self.render_hotbar(surface)

    def render_hotbar(self, surface: pygame.Surface):
        """Draw a minimal hotbar for the player inventory."""
        slot_size = 32
        padding = 6
        total_slots = self.player.inventory.hotbar_size
        total_width = total_slots * slot_size + (total_slots - 1) * padding
        start_x = (surface.get_width() - total_width) // 2
        y = surface.get_height() - slot_size - 12
        font = pygame.font.SysFont(None, 20)
        for i in range(total_slots):
            x = start_x + i * (slot_size + padding)
            rect = pygame.Rect(x, y, slot_size, slot_size)
            pygame.draw.rect(surface, (30, 30, 30), rect)
            border_color = (
                (255, 255, 255)
                if i == self.player.inventory.selected_index
                else (120, 120, 120)
            )
            pygame.draw.rect(surface, border_color, rect, 2)
            stack = self.player.inventory.slots[i]
            if stack is not None:
                text = font.render(str(stack.count), True, (220, 220, 220))
                surface.blit(text, (x + 4, y + 8))
