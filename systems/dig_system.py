import math

from entities.item_drop import ItemDrop
from entities.itemreg import ITEMREG_TABLE
from settings import DIG_BASE_TIME, PICKUP_RADIUS, TILE_SIZE
from world.tilereg import TILEREG_TABLE, TILE_DROPS


class DigState:
    def __init__(self):
        self.target = None
        self.timer = 0.0
        self.required = 0.0


class DigSystem:
    def __init__(self, world, entity_manager):
        """Handle tile digging and drops for players."""
        self.world = world
        self.entity_manager = entity_manager
        self.states: dict[object, DigState] = {}

    def update(self, player, input_frame, dt: float):
        """Process digging input for the player."""
        if player is None or not player.is_alive:
            return
        state = self.states.setdefault(player, DigState())
        if player.backpack.is_open:
            self.reset_state(state)
            return
        if 1 in input_frame.mouse_buttons_held:
            selected = player.inventory.get_selected()
            item_def = ITEMREG_TABLE.get(selected.item_id, {}) if selected else {}
            tool = item_def.get("tool") if selected else None
            if tool is None or not tool.can_dig:
                self.reset_state(state)
                return
            mx, my = input_frame.mouse_pos
            world_x, world_y = player.screen_to_world(mx, my)
            if (
                math.hypot(world_x - player.pos[0], world_y - player.pos[1])
                > PICKUP_RADIUS
            ):
                self.reset_state(state)
                return
            tile_id = self.world.get_tile_at(world_x, world_y)
            if tile_id is None or tile_id == 0:
                self.reset_state(state)
                return
            tile_x = (world_x // TILE_SIZE) * TILE_SIZE
            tile_y = (world_y // TILE_SIZE) * TILE_SIZE
            target = (tile_x, tile_y)
            if target != state.target:
                state.target = target
                state.timer = 0.0
                hardness = TILEREG_TABLE[tile_id]["hardness"]
                state.required = tool.dig_time(hardness, DIG_BASE_TIME)
            state.timer += dt
            if state.timer >= state.required:
                self.break_tile(player, tile_x, tile_y, tile_id)
                self.reset_state(state)
        if 1 in input_frame.mouse_buttons_released:
            self.reset_state(state)

    def break_tile(self, player, tile_x: float, tile_y: float, tile_id: int):
        """Remove a tile and spawn a drop."""
        drop_id = TILE_DROPS.get(tile_id)
        if drop_id is not None:
            if self.entity_manager is not None:
                self.entity_manager.add_entity(ItemDrop(tile_x, tile_y, drop_id, 1))
            else:
                player.inventory.add_item(drop_id, 1)
        self.world.set_tile_at(tile_x, tile_y, 0)

    def get_progress(self, player):
        """Return dig target and progress ratio (0.0-1.0)."""
        state = self.states.get(player)
        if state is None or state.target is None or state.required <= 0:
            return None, 0.0
        return state.target, min(1.0, state.timer / state.required)

    @staticmethod
    def reset_state(state: DigState):
        """Clear digging state."""
        state.target = None
        state.timer = 0.0
        state.required = 0.0
