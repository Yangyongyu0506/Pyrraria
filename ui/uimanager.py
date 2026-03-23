from ui.health import HealthBar
from entities.player import Player
from utils.maths import world_to_screen
import pygame


class UIManager:
    def __init__(self, player: Player, dig_system):
        """Create and manage UI widgets."""
        self.health_bar = HealthBar(player)
        self.player = player
        self.dig_system = dig_system

    def update(self, dt: float):
        """Update UI widget states."""
        self.health_bar.update(dt)

    def render(self, surface: pygame.Surface):
        """Render UI widgets to the screen."""
        self.health_bar.render(surface)
        self.player.inventory.render(surface)
        self.player.backpack.render(surface)
        self.render_dig_ui(surface)

    def render_dig_ui(self, surface: pygame.Surface):
        """Draw digging progress UI when active."""
        target, ratio = self.dig_system.get_progress(self.player)
        if target is None:
            return
        tile_x, tile_y = target
        screen_x, screen_y = world_to_screen(
            tile_x,
            tile_y,
            self.player.world.camx,
            self.player.world.camy,
        )
        bar_width = 32
        bar_height = 6
        bar_x = int(screen_x)
        bar_y = int(screen_y - 10)
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        fg_rect = pygame.Rect(bar_x, bar_y, int(bar_width * ratio), bar_height)
        pygame.draw.rect(surface, (0, 0, 0), bg_rect)
        pygame.draw.rect(surface, (220, 200, 80), fg_rect)
        pygame.draw.rect(surface, (255, 255, 255), bg_rect, 1)
