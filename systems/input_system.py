import pygame


class InputSystem:
    def __init__(self, dig_system, pickup_system, placement_system, discard_system):
        """Handle high-level input mappings for the player."""
        self.dig_system = dig_system
        self.pickup_system = pickup_system
        self.placement_system = placement_system
        self.discard_system = discard_system

    def update(self, player, input_frame, dt: float):
        """Apply input actions to player state."""
        if player is None or not player.is_alive or input_frame is None:
            return
        if pygame.K_e in input_frame.keys_pressed:
            player.backpack.toggle()

        if player.backpack.is_open:
            if pygame.K_h in input_frame.keys_pressed:
                player.backpack.move_cursor(-1, 0)
            if pygame.K_l in input_frame.keys_pressed:
                player.backpack.move_cursor(1, 0)
            if pygame.K_k in input_frame.keys_pressed:
                player.backpack.move_cursor(0, -1)
            if pygame.K_j in input_frame.keys_pressed:
                player.backpack.move_cursor(0, 1)

            if pygame.K_1 in input_frame.keys_pressed:
                player.backpack.swap_with_inventory(player.inventory, 0)
            if pygame.K_2 in input_frame.keys_pressed:
                player.backpack.swap_with_inventory(player.inventory, 1)
            if pygame.K_3 in input_frame.keys_pressed:
                player.backpack.swap_with_inventory(player.inventory, 2)
            if pygame.K_4 in input_frame.keys_pressed:
                player.backpack.swap_with_inventory(player.inventory, 3)
            if pygame.K_5 in input_frame.keys_pressed:
                player.backpack.swap_with_inventory(player.inventory, 4)
            if pygame.K_6 in input_frame.keys_pressed:
                player.backpack.swap_with_inventory(player.inventory, 5)
            if pygame.K_7 in input_frame.keys_pressed:
                player.backpack.swap_with_inventory(player.inventory, 6)
            if pygame.K_8 in input_frame.keys_pressed:
                player.backpack.swap_with_inventory(player.inventory, 7)
            if pygame.K_9 in input_frame.keys_pressed:
                player.backpack.swap_with_inventory(player.inventory, 8)
        else:
            if pygame.K_1 in input_frame.keys_pressed:
                player.inventory.select_slot(0)
            if pygame.K_2 in input_frame.keys_pressed:
                player.inventory.select_slot(1)
            if pygame.K_3 in input_frame.keys_pressed:
                player.inventory.select_slot(2)
            if pygame.K_4 in input_frame.keys_pressed:
                player.inventory.select_slot(3)
            if pygame.K_5 in input_frame.keys_pressed:
                player.inventory.select_slot(4)
            if pygame.K_6 in input_frame.keys_pressed:
                player.inventory.select_slot(5)
            if pygame.K_7 in input_frame.keys_pressed:
                player.inventory.select_slot(6)
            if pygame.K_8 in input_frame.keys_pressed:
                player.inventory.select_slot(7)
            if pygame.K_9 in input_frame.keys_pressed:
                player.inventory.select_slot(8)

        moving_left = pygame.K_a in input_frame.keys_held
        moving_right = pygame.K_d in input_frame.keys_held
        on_ground = player.is_on_ground()
        if moving_left and not moving_right:
            player.vel[0] = -player.move_speed
        elif moving_right and not moving_left:
            player.vel[0] = player.move_speed
        else:
            friction = player.ground_friction if on_ground else player.air_friction
            player.vel[0] -= player.vel[0] * min(1.0, friction * dt)

        jump_pressed = (
            pygame.K_SPACE in input_frame.keys_pressed
            or pygame.K_w in input_frame.keys_pressed
        )
        if jump_pressed and on_ground:
            player.vel[1] = -player.jump_speed

        self.dig_system.update(player, input_frame, dt)
        self.placement_system.update(player, input_frame)
        self.discard_system.update(player, input_frame)
        self.pickup_system.update(player)
