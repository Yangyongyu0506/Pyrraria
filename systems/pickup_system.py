from entities.item_drop import ItemDrop
from settings import PICKUP_COLLECT_RADIUS, PICKUP_RADIUS


class PickupSystem:
    def __init__(self, entity_manager):
        """Handle item drop attraction and pickup."""
        self.entity_manager = entity_manager

    def update(self, player):
        """Pull nearby drops to the player and collect them."""
        if player is None or not player.is_alive:
            return
        attract_sq = PICKUP_RADIUS * PICKUP_RADIUS
        collect_sq = PICKUP_COLLECT_RADIUS * PICKUP_COLLECT_RADIUS
        for entity in self.entity_manager.entities:
            if not isinstance(entity, ItemDrop):
                continue
            dx = (entity.pos[0] + entity.width / 2) - (player.pos[0] + player.width / 2)
            dy = (entity.pos[1] + entity.height / 2) - (
                player.pos[1] + player.height / 2
            )
            dist_sq = dx * dx + dy * dy
            if collect_sq < dist_sq <= attract_sq:
                target_x = player.pos[0] + player.width / 2 - entity.width / 2
                target_y = player.pos[1] + player.height / 2 - entity.height / 2
                entity.start_pickup(target_x, target_y)
            elif dist_sq > attract_sq:
                continue
            elif dist_sq <= collect_sq:
                remaining = player.inventory.add_item(entity.item_id, entity.count)
                if remaining == 0:
                    entity.is_alive = False
                else:
                    entity.count = remaining
