from entities.entity import Entity
from entities.item_drop import ItemDrop
from entities.player import Player
from world.world import World
from settings import MAX_ENTITIES, PICKUP_COLLECT_RADIUS, PICKUP_RADIUS, TILE_SIZE


class EntityManager:
    def __init__(self, world: World, max_entities: int = MAX_ENTITIES):
        """Manage entity lifecycle, updates, and collisions."""
        self.world = world
        self.entities = []
        self.max_entities = max_entities

    def add_entity(self, entity: Entity):
        """Add an entity if capacity allows."""
        if len(self.entities) < self.max_entities:
            self.entities.append(entity)
        else:
            # process conflicts
            pass

    def remove_entity(self, entity: Entity):
        """Remove an entity and trigger its death hook."""
        if entity in self.entities:
            entity.on_dead()
            self.entities.remove(entity)

    def update(self, dt, input_frame=None):
        """Update all entities, resolve collisions, and clean up dead ones."""
        for entity in self.entities:
            if input_frame is not None and hasattr(entity, "update"):
                entity.update(input_frame, dt)
            else:
                entity.update_pos(dt)
        self.solve_collisions(dt)
        self.collect_item_drops()
        for entity in self.entities:
            if hasattr(entity, "post_update"):
                entity.post_update(dt)
        self.entities = [entity for entity in self.entities if entity.is_alive]

    def collect_item_drops(self, pickup_radius: float = PICKUP_RADIUS):
        """Collect nearby item drops into the player's inventory."""
        player = next(
            (entity for entity in self.entities if isinstance(entity, Player)), None
        )
        if player is None:
            return
        radius_sq = pickup_radius * pickup_radius
        collect_sq = PICKUP_COLLECT_RADIUS * PICKUP_COLLECT_RADIUS
        for entity in self.entities:
            if not isinstance(entity, ItemDrop):
                continue
            dx = (entity.pos[0] + entity.width / 2) - (player.pos[0] + player.width / 2)
            dy = (entity.pos[1] + entity.height / 2) - (
                player.pos[1] + player.height / 2
            )
            dist_sq = dx * dx + dy * dy
            if dist_sq <= radius_sq:
                target_x = player.pos[0] + player.width / 2 - entity.width / 2
                target_y = player.pos[1] + player.height / 2 - entity.height / 2
                entity.start_pickup(target_x, target_y)
            if dist_sq > collect_sq:
                continue
            remaining = player.inventory.add_item(entity.item_id, entity.count)
            if remaining == 0:
                entity.is_alive = False
            else:
                entity.count = remaining

    def solve_collisions(self, dt):
        """Resolve entity collisions against solid world tiles."""
        for entity in self.entities:
            if entity.is_noclip:
                continue
            if not entity.hitboxes:
                continue
            entity.did_land = False
            entity.landed_speed = 0.0
            prev_x, prev_y = entity.prev_pos
            next_x, next_y = entity.pos
            prev_vel_y = entity.vel[1]
            # X axis
            entity.pos[0] = next_x
            entity.pos[1] = prev_y
            rects_x = [
                hitbox.get_rect(entity.pos[0], entity.pos[1])
                for hitbox in entity.hitboxes
            ]
            if any(self.world.is_rect_solid(rect) for rect in rects_x):
                delta_x = next_x - prev_x
                if delta_x > 0:
                    resolved_x = next_x
                    for hitbox in entity.hitboxes:
                        rect = hitbox.get_rect(next_x, prev_y)
                        tile_x = (rect.right - 1) // TILE_SIZE
                        resolved_x = min(
                            resolved_x, tile_x * TILE_SIZE - hitbox.x - hitbox.width
                        )
                    entity.pos[0] = resolved_x
                else:
                    resolved_x = next_x
                    for hitbox in entity.hitboxes:
                        rect = hitbox.get_rect(next_x, prev_y)
                        tile_x = rect.left // TILE_SIZE
                        resolved_x = max(
                            resolved_x, (tile_x + 1) * TILE_SIZE - hitbox.x
                        )
                    entity.pos[0] = resolved_x
                entity.vel[0] = 0.0
            # Y axis
            entity.pos[0] = entity.pos[0]
            entity.pos[1] = next_y
            rects_y = [
                hitbox.get_rect(entity.pos[0], entity.pos[1])
                for hitbox in entity.hitboxes
            ]
            if any(self.world.is_rect_solid(rect) for rect in rects_y):
                delta_y = next_y - prev_y
                if delta_y > 0:
                    resolved_y = next_y
                    for hitbox in entity.hitboxes:
                        rect = hitbox.get_rect(entity.pos[0], next_y)
                        tile_y = (rect.bottom - 1) // TILE_SIZE
                        resolved_y = min(
                            resolved_y, tile_y * TILE_SIZE - hitbox.y - hitbox.height
                        )
                    entity.pos[1] = resolved_y
                    entity.did_land = True
                    entity.landed_speed = prev_vel_y
                else:
                    resolved_y = next_y
                    for hitbox in entity.hitboxes:
                        rect = hitbox.get_rect(entity.pos[0], next_y)
                        tile_y = rect.top // TILE_SIZE
                        resolved_y = max(
                            resolved_y, (tile_y + 1) * TILE_SIZE - hitbox.y
                        )
                    entity.pos[1] = resolved_y
                entity.vel[1] = 0.0

    def render(self, screen, camera):
        """Render all entities to the screen."""
        for entity in self.entities:
            entity.render(screen, camera)

    def on_exit(self):
        """Invoke entity shutdown logic and clear the list."""
        for entity in self.entities:
            entity.on_dead()
        self.entities.clear()

    def find_empty_spawn(self, width_px: int, height_px: int, max_tries: int = 300):
        """Find a non-solid spawn location via the world helper."""
        return self.world.find_empty_spawn(width_px, height_px, max_tries)
