class PhysicsSystem:
    def __init__(self):
        """Handle physics constraints and integration."""

    def update(self, player, dt: float):
        """Apply physics clamps to the player."""
        if player is None or not player.is_alive:
            return
        if player.vel[1] > player.max_fall_speed:
            player.vel[1] = player.max_fall_speed
