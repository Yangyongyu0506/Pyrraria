from entities.entity import Entity
from world.world import World
from settings import MAX_ENTITIES


class EntityManager:
    def __init__(self, world: World, max_entities: int = MAX_ENTITIES):
        self.world = world
        self.entities = []
        self.max_entities = max_entities

    def add_entity(self, entity: Entity):
        if len(self.entities) < self.max_entities:
            self.entities.append(entity)
        else:
            # process conflicts
            pass

    def remove_entity(self, entity: Entity):
        if entity in self.entities:
            entity.on_dead()
            self.entities.remove(entity)

    def update(self, dt, input_frame=None):
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
                entity.pos[1] = prev_y
                if prev_vel_y > 0:
                    entity.did_land = True
                    entity.landed_speed = prev_vel_y
                entity.vel[1] = 0.0

    def render(self, screen, camera):
        for entity in self.entities:
            entity.render(screen, camera)

    def on_exit(self):
        for entity in self.entities:
            entity.on_dead()
        self.entities.clear()

    def find_empty_spawn(self, width_px: int, height_px: int, max_tries: int = 300):
        return self.world.find_empty_spawn(width_px, height_px, max_tries)
