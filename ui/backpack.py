import os

import pygame

from settings import DIR_ROOT
from ui.inventory import Inventory, ItemStack
from entities.itemreg import ITEMREG_TABLE


class Backpack(Inventory):
    """Extended storage that mirrors the Inventory interface."""

    def __init__(
        self,
        slot_count: int = 30,
        hotbar_size: int = 30,
        max_stack: int = 99,
    ):
        save_path = os.path.join(DIR_ROOT, "user/player/backpack.json")
        super().__init__(
            slot_count=slot_count,
            hotbar_size=hotbar_size,
            max_stack=max_stack,
            save_path=save_path,
        )
        self.is_open = False
        self.cursor_index = 0
        self.columns = 10

    def toggle(self):
        """Toggle backpack visibility."""
        self.is_open = not self.is_open

    def move_cursor(self, dx: int, dy: int):
        """Move cursor in a grid layout."""
        if not self.is_open:
            return
        rows = max(1, (len(self.slots) + self.columns - 1) // self.columns)
        col = self.cursor_index % self.columns
        row = self.cursor_index // self.columns
        col = max(0, min(self.columns - 1, col + dx))
        row = max(0, min(rows - 1, row + dy))
        next_index = row * self.columns + col
        if next_index >= len(self.slots):
            next_index = len(self.slots) - 1
        self.cursor_index = next_index

    def swap_with_inventory(self, inventory: Inventory, hotbar_index: int):
        """Swap the cursor slot with an inventory hotbar slot."""
        if not self.is_open:
            return
        if not (0 <= hotbar_index < inventory.hotbar_size):
            return
        backpack_stack = self.slots[self.cursor_index]
        inventory_stack = inventory.slots[hotbar_index]
        self.slots[self.cursor_index] = inventory_stack
        inventory.slots[hotbar_index] = backpack_stack

    def render(self, surface: pygame.Surface):
        """Render the backpack grid if open."""
        if not self.is_open:
            return
        slot_size = 32
        padding = 6
        columns = self.columns
        rows = max(1, (len(self.slots) + columns - 1) // columns)
        total_width = columns * slot_size + (columns - 1) * padding
        total_height = rows * slot_size + (rows - 1) * padding
        start_x = 24
        start_y = 48
        panel_rect = pygame.Rect(
            start_x - 12,
            start_y - 12,
            total_width + 24,
            total_height + 24,
        )
        pygame.draw.rect(surface, (20, 20, 20), panel_rect)
        pygame.draw.rect(surface, (140, 140, 140), panel_rect, 2)
        for i in range(len(self.slots)):
            row = i // columns
            col = i % columns
            x = start_x + col * (slot_size + padding)
            y = start_y + row * (slot_size + padding)
            rect = pygame.Rect(x, y, slot_size, slot_size)
            pygame.draw.rect(surface, (30, 30, 30), rect)
            border_color = (
                (255, 255, 255) if i == self.cursor_index else (120, 120, 120)
            )
            pygame.draw.rect(surface, border_color, rect, 2)
            stack: ItemStack | None = self.slots[i]
            if stack is not None:
                pygame.draw.rect(
                    surface,
                    ITEMREG_TABLE[stack.item_id]["color"],
                    rect.inflate(-4, -4),
                )
                text = self.font.render(str(stack.count), True, (220, 220, 220))
                surface.blit(text, (x + 4, y + 8))
                if i == self.cursor_index:
                    text = self.font.render(
                        ITEMREG_TABLE[stack.item_id]["name"], True, (255, 255, 255)
                    )
                    surface.blit(text, (start_x, start_y + total_height + 8))
