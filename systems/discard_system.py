import pygame


class DiscardSystem:
    def __init__(self, entity_manager):
        """Handle dropping items from the backpack."""
        self.entity_manager = entity_manager

    def update(self, player, input_frame):
        """Process discard input while the backpack is open."""
        if player is None or not player.is_alive:
            return
        if not player.backpack.is_open:
            return
        if input_frame is None:
            return
        if pygame.K_q in input_frame.keys_pressed:
            player.backpack.discard(
                self.entity_manager, (float(player.pos[0]), float(player.pos[1]))
            )
