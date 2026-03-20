import pygame
from threading import Thread
import time
import logging
from core.camera import Camera
from utils.maths import world_to_screen
from settings import (
    CHUNK_PX,
    TILE_SIZE,
    WORLD_CHUNK_WIDTH,
    WORLD_CHUNK_HEIGHT,
    CHUNK_LOAD_RADIUS,
    DIR_ROOT,
    WORLD_W_PX,
    WORLD_H_PX,
)
from world.chunkmanager import ChunkManager
from world.generator import Generator


class World:
    def __init__(self, name: str = "new_world", logger: logging.Logger | None = None):
        """Manage world state, chunk streaming, and rendering."""
        self.name = name
        self.generator = Generator(world_name=self.name)
        self.chunk_manager = ChunkManager(self, generator=self.generator)
        self.logger = logger or logging.getLogger("pyrraria.world")
        self.camx, self.camy = (
            WORLD_W_PX // 2,
            WORLD_H_PX // 2,
        )
        self.load_background()
        self.chunk_io_thread = Thread(target=self.chunk_io, daemon=True)
        self.chunk_io_thread.start()
        self.spawn_x, self.spawn_y = self.load_spawn_point()

    def load_background(self):
        """Load the world background texture and reset cached scale."""
        self.background_img = pygame.image.load(
            f"{DIR_ROOT}/assets/backgrounds/day.png"
        ).convert_alpha()
        self.background_scaled = None
        self.background_scaled_size = None

    def set_campos(self, x, y):
        """Update the camera's world-space position for streaming."""
        self.camx = x
        self.camy = y

    def get_chunk(self, cx, cy):
        """Return a loaded chunk at the given indices."""
        return self.chunk_manager.get_chunk(cx, cy)

    def load_chunk(self, cx, cy):
        """Load or generate a chunk into memory."""
        return self.chunk_manager.load_chunk(cx, cy)

    def unload_chunk(self, cx, cy):
        """Unload and persist a chunk from memory."""
        self.chunk_manager.unload_chunk(cx, cy)

    def update(self, player_pos):
        """Update streaming center based on player position."""
        self.set_campos(*player_pos)

    def chunk_io(self):
        """Background thread: load nearby chunks and unload distant ones."""
        while True:
            pcx = (self.camx // CHUNK_PX) % WORLD_CHUNK_WIDTH
            pcy = self.camy // CHUNK_PX % WORLD_CHUNK_HEIGHT
            for cy in range(pcy - CHUNK_LOAD_RADIUS, pcy + CHUNK_LOAD_RADIUS + 1):
                for cx in range(pcx - CHUNK_LOAD_RADIUS, pcx + CHUNK_LOAD_RADIUS + 1):
                    cx_wrap = cx % WORLD_CHUNK_WIDTH
                    cy_wrap = cy % WORLD_CHUNK_HEIGHT
                    if self.get_chunk(cx_wrap, cy_wrap) is None:
                        self.logger.info(f"Loading chunk ({cx_wrap}, {cy_wrap})")
                        self.load_chunk(cx_wrap, cy_wrap)
            unload_list = []
            for pos, _chunk in self.chunk_manager.all_chunks():
                cx, cy = pos
                dx = abs(cx - pcx)
                dx = min(dx, WORLD_CHUNK_WIDTH - dx)
                dy = abs(cy - pcy)
                dy = min(dy, WORLD_CHUNK_HEIGHT - dy)
                if dx > CHUNK_LOAD_RADIUS or dy > CHUNK_LOAD_RADIUS:
                    unload_list.append((cx, cy))
            for pos in unload_list:
                self.logger.info(f"Unloading chunk {pos}")
                self.unload_chunk(*pos)
            time.sleep(0.5)

    def render(self, screen: pygame.Surface, camera: Camera):
        """Draw the background and visible chunks."""
        screen_w, screen_h = screen.get_size()
        if self.background_scaled_size != (screen_w, screen_h):
            self.background_scaled = pygame.transform.scale(
                self.background_img, (screen_w, screen_h)
            )
            self.background_scaled_size = (screen_w, screen_h)
        if self.background_scaled is not None:
            screen.blit(self.background_scaled, (0, 0))
        camx = int(camera.x)
        camy = int(camera.y)
        screen_w = screen.get_width()
        screen_h = screen.get_height()
        start_cx = camx // CHUNK_PX
        start_cy = camy // CHUNK_PX
        end_cx = start_cx + screen_w // CHUNK_PX + 2
        end_cy = start_cy + screen_h // CHUNK_PX + 2
        for cy in range(start_cy, end_cy):
            for cx in range(start_cx, end_cx):
                # Ensure coordinates wrap around world boundaries
                cx_wrap = cx % (WORLD_CHUNK_WIDTH)
                cy_wrap = cy % WORLD_CHUNK_HEIGHT
                chunk = self.get_chunk(cx_wrap, cy_wrap)
                if chunk is None:
                    logging.warning(
                        f"Chunk ({cx_wrap}, {cy_wrap}) not loaded."
                    )  # Debugging
                    continue
                surface = chunk.surface()
                if surface is None:
                    logging.warning(
                        f"Chunk ({cx_wrap}, {cy_wrap}) has no surface."
                    )  # Debugging
                    continue
                world_x = cx * CHUNK_PX  # use cx instead of cx_wrap
                world_y = cy * CHUNK_PX
                screen_x, screen_y = world_to_screen(world_x, world_y, camx, camy)
                screen.blit(surface, (screen_x, screen_y))

    def set_tile_at(self, world_x, world_y, tile_id):
        """Set a tile at world coordinates with wraparound."""
        world_x = world_x % WORLD_W_PX
        world_y = world_y % WORLD_H_PX
        self.chunk_manager.set_tile_at(world_x, world_y, tile_id)

    def get_tile_at(self, world_x, world_y):
        """Return the tile id at world coordinates, or None if unloaded."""
        world_x = world_x % WORLD_W_PX
        world_y = world_y % WORLD_H_PX
        cx = (world_x // CHUNK_PX) % WORLD_CHUNK_WIDTH
        cy = (world_y // CHUNK_PX) % WORLD_CHUNK_HEIGHT
        chunk = self.get_chunk(cx, cy)
        if not chunk:
            return None
        local_x = (world_x % CHUNK_PX) // TILE_SIZE
        local_y = (world_y % CHUNK_PX) // TILE_SIZE
        return int(chunk.tiles[local_y, local_x])

    def is_solid_at(self, world_x, world_y):
        """Check if a world-space tile is solid."""
        world_x = world_x % WORLD_W_PX
        world_y = world_y % WORLD_H_PX
        cx = (world_x // CHUNK_PX) % WORLD_CHUNK_WIDTH
        cy = (world_y // CHUNK_PX) % WORLD_CHUNK_HEIGHT
        chunk = self.get_chunk(cx, cy)
        if chunk:
            local_x = (world_x % CHUNK_PX) // TILE_SIZE
            local_y = (world_y % CHUNK_PX) // TILE_SIZE
            return chunk.is_solid_at(local_x, local_y)
        return False

    def is_rect_solid(self, rect: pygame.Rect) -> bool:
        """Check if a world-space rectangle overlaps any solid tile."""
        left = rect.left
        right = rect.right
        top = rect.top
        bottom = rect.bottom
        if right <= left or bottom <= top:
            return False
        tile_left = left // TILE_SIZE
        tile_right = (right - 1) // TILE_SIZE
        tile_top = top // TILE_SIZE
        tile_bottom = (bottom - 1) // TILE_SIZE
        for tx in range(tile_left, tile_right + 1):
            for ty in range(tile_top, tile_bottom + 1):
                wx = tx * TILE_SIZE
                wy = ty * TILE_SIZE
                if self.is_solid_at(wx, wy):
                    return True
        return False

    def on_exit(self):
        """Persist loaded chunks on shutdown."""
        for pos, chunk in self.chunk_manager.all_chunks():
            chunk.save(self.name)
            self.logger.info(f"Unloading chunk {pos}")
        self.chunk_manager.on_exit()

    def find_empty_spawn(
        self, width_px: int, height_px: int, max_tries: int = 300
    ) -> tuple[int, int]:
        """Search for a non-solid spawn position near world center."""
        world_w = WORLD_W_PX
        world_h = WORLD_H_PX
        spawn_center_x = world_w // 2
        spawn_center_y = world_h // 2
        step = TILE_SIZE

        for i in range(max_tries):
            dx = (i % 20 - 10) * step
            dy = (i // 20 - 10) * step
            x = (spawn_center_x + dx) % world_w
            y = (spawn_center_y + dy) % world_h
            rect = pygame.Rect(x, y, width_px, height_px)
            if not self.is_rect_solid(rect):
                return x, y

        return spawn_center_x, spawn_center_y

    def load_spawn_point(self) -> tuple[int, int]:
        """Load a persisted spawn point or fall back to a safe location."""
        path = f"{DIR_ROOT}/user/world_data/{self.name}/spawn_point.txt"
        try:
            with open(path, "r") as f:
                spawn_x, spawn_y = map(int, f.read().split(","))
            return spawn_x * TILE_SIZE, spawn_y * TILE_SIZE
        except (FileNotFoundError, ValueError):
            return self.find_empty_spawn(TILE_SIZE, 2 * TILE_SIZE)
