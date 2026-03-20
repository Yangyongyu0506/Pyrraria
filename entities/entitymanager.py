from entities.entity import Entity
from world.world import World
from settings import MAX_ENTITIES, TILE_SIZE


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
        for entity in self.entities:
            if hasattr(entity, "post_update"):
                entity.post_update(dt)
        self.entities = [entity for entity in self.entities if entity.is_alive]

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
                step_dir = 1 if (next_x - prev_x) > 0 else -1
                steps = 0
                while (
                    any(self.world.is_rect_solid(rect) for rect in rects_x)
                    and steps < TILE_SIZE
                ):
                    entity.pos[0] -= step_dir
                    rects_x = [
                        hitbox.get_rect(entity.pos[0], entity.pos[1])
                        for hitbox in entity.hitboxes
                    ]
                    steps += 1
                if any(self.world.is_rect_solid(rect) for rect in rects_x):
                    entity.pos[0] = prev_x
                entity.vel[0] = 0.0
            # Y axis
            entity.pos[0] = entity.pos[0]
            entity.pos[1] = next_y
            rects_y = [
                hitbox.get_rect(entity.pos[0], entity.pos[1])
                for hitbox in entity.hitboxes
            ]
            if any(self.world.is_rect_solid(rect) for rect in rects_y):
                step_dir = 1 if (next_y - prev_y) > 0 else -1
                steps = 0
                while (
                    any(self.world.is_rect_solid(rect) for rect in rects_y)
                    and steps < TILE_SIZE
                ):
                    entity.pos[1] -= step_dir
                    rects_y = [
                        hitbox.get_rect(entity.pos[0], entity.pos[1])
                        for hitbox in entity.hitboxes
                    ]
                    steps += 1
                if any(self.world.is_rect_solid(rect) for rect in rects_y):
                    entity.pos[1] = prev_y
                if prev_vel_y > 0:
                    entity.did_land = True
                    entity.landed_speed = prev_vel_y
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
