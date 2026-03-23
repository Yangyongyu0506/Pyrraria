import math

from entities.itemreg import ITEMREG_TABLE
from settings import PICKUP_RADIUS


class PlacementSystem:
    def __init__(self, world):
        """Handle placing tiles from inventory."""
        self.world = world

    def update(self, player, input_frame):
        """Process right-click placement for the player."""
        if player is None or not player.is_alive:
            return
        if player.backpack.is_open:
            return
        if 3 not in input_frame.mouse_buttons_pressed:
            return
        selected = player.inventory.get_selected()
        if (
            selected is None
            or selected.count <= 0
            or not ITEMREG_TABLE[selected.item_id]["placeable"]
        ):
            return
        mx, my = input_frame.mouse_pos
        world_x, world_y = player.screen_to_world(mx, my)
        if math.hypot(world_x - player.pos[0], world_y - player.pos[1]) > PICKUP_RADIUS:
            return
        if self.world.get_tile_at(world_x, world_y) == 0:
            self.world.set_tile_at(world_x, world_y, selected.item_id)
            player.inventory.remove_selected(1)
