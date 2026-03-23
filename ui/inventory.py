from dataclasses import dataclass

import pygame
from settings import DIR_ROOT
import json
import os

from world.itemreg import ITEMREG_TABLE


@dataclass
class ItemStack:
    """Represents a stack of identical items."""

    item_id: int
    count: int


class Inventory:
    """Simple fixed-size inventory with a selectable hotbar."""

    def __init__(self, slot_count: int = 20, hotbar_size: int = 9, max_stack: int = 99):
        self.slots: list[ItemStack | None] = [None] * slot_count
        self.hotbar_size = min(hotbar_size, slot_count)
        self.max_stack = max_stack
        self.selected_index = 0
        self.save_path = os.path.join(DIR_ROOT, "user/player/inventory.json")
        self.load_items(self.save_path)

    def select_slot(self, index: int):
        """Select a hotbar slot by index."""
        if 0 <= index < self.hotbar_size:
            self.selected_index = index

    def get_selected(self) -> ItemStack | None:
        """Return the currently selected stack, if any."""
        return self.slots[self.selected_index]

    def add_item(self, item_id: int, count: int = 1) -> int:
        """Add items to inventory; returns leftover count not stored."""
        if item_id <= 0 or count <= 0:
            return count
        remaining = count
        for slot in self.slots:
            if slot and slot.item_id == item_id and slot.count < self.max_stack:
                space = self.max_stack - slot.count
                to_add = min(space, remaining)
                slot.count += to_add
                remaining -= to_add
                if remaining == 0:
                    return 0
        for i, slot in enumerate(self.slots):
            if slot is None:
                to_add = min(self.max_stack, remaining)
                self.slots[i] = ItemStack(item_id=item_id, count=to_add)
                remaining -= to_add
                if remaining == 0:
                    return 0
        return remaining

    def remove_selected(self, count: int = 1) -> bool:
        """Remove items from the selected stack; returns True if removed."""
        if count <= 0:
            return False
        stack = self.get_selected()
        if stack is None or stack.count < count:
            return False
        stack.count -= count
        if stack.count == 0:
            self.slots[self.selected_index] = None
        return True
    
    def load_items(self, path: str | None = None):
        """Load inventory items from a json file."""
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                for i, entry in enumerate(data):
                    if entry is not None:
                        self.slots[i] = ItemStack(
                            item_id=entry["item_id"], count=entry["count"]
                        )

    def write_items(self, path: str | None = None):
        """Write inventory items to a json file."""
        data = []
        for slot in self.slots:
            if slot is not None:
                data.append({"item_id": slot.item_id, "count": slot.count})
            else:
                data.append(None)
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        with open(path, "w") as f:
            json.dump(data, f)

    def render(self, surface: pygame.Surface):
        """Draw a minimal hotbar for the player inventory."""
        slot_size = 32
        padding = 6
        total_slots = self.hotbar_size
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
                if i == self.selected_index
                else (120, 120, 120)
            )
            pygame.draw.rect(surface, border_color, rect, 2)
            stack = self.slots[i]
            if stack is not None:
                pygame.draw.rect(
                    surface,
                    ITEMREG_TABLE[stack.item_id]["color"],
                    rect.inflate(-4, -4),
                )
                text = font.render(str(stack.count), True, (220, 220, 220))
                surface.blit(text, (x + 4, y + 8))


    def on_exit(self):
        """Save inventory items to json files."""
        self.write_items(self.save_path)