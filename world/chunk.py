import numpy as np
import pygame
import logging
from settings import CHUNK_SIZE, TILE_SIZE, DIR_ROOT
from world.tilereg import TILEREG_TABLE


class Chunk:
    def __init__(
        self, cx: int, cy: int, size: int = CHUNK_SIZE, tile_size: int = TILE_SIZE
    ):
        assert cx >= 0 and cy >= 0, "Chunk coordinates must be non-negative"
        self.cx = cx
        self.cy = cy
        self.size = size
        self.tile_size = tile_size
        self.tiles = np.zeros((size, size), dtype=np.uint8)
        self.dirty = False  # marks if the chunk needs to be re-rendered
        self.surface_cache = None  # cached surface for rendering

    def set_tile(self, x: int, y: int, tile_id: int):
        if 0 <= x < CHUNK_SIZE and 0 <= y < CHUNK_SIZE:
            self.tiles[y, x] = tile_id
            self.dirty = True

    def load(self, world_name: str = "new_world") -> bool:
        """
        load chunk data from disk, for example when it's near the player
        """
        path = f"{DIR_ROOT}/user/world_data/{world_name}/chunk_{self.cx}_{self.cy}.npy"
        try:
            self.tiles = np.load(path)
            self.dirty = False
            return True
        except FileNotFoundError:
            # if file not found, initialize with empty tiles
            self.tiles = np.zeros((CHUNK_SIZE, CHUNK_SIZE), dtype=np.uint8)
            self.dirty = True
            return False

    def save(self, world_name: str = "new_world"):
        """
        save chunk data to disk
        """
        if self.dirty:
            path = (
                f"{DIR_ROOT}/user/world_data/{world_name}/chunk_{self.cx}_{self.cy}.npy"
            )
            np.save(path, self.tiles)
            self.dirty = False

    def draw_tile(self, tile_id, surf: pygame.Surface, rect: pygame.Rect, debug: bool):
        if tile_id == 0:
            return
        tile = TILEREG_TABLE[tile_id]
        color = tile["color"]
        if debug:
            pygame.draw.rect(surf, (255, 0, 255, 255), rect)
        else:
            pygame.draw.rect(surf, color, rect)

    def surface(self, debug: bool = False) -> pygame.Surface:
        if not self.dirty and self.surface_cache is not None:
            return self.surface_cache
        size = CHUNK_SIZE * TILE_SIZE
        surf = pygame.Surface((size, size), pygame.SRCALPHA).convert_alpha()
        surf.fill((0, 0, 0, 0))  # transparent
        for y in range(CHUNK_SIZE):
            for x in range(CHUNK_SIZE):
                tile_id = self.tiles[y, x]
                if debug and tile_id == 0:
                    continue
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                self.draw_tile(
                    tile_id,
                    surf,
                    rect,
                    debug
                    and (
                        x == 0 or y == 0 or x == CHUNK_SIZE - 1 or y == CHUNK_SIZE - 1
                    ),
                )
        if debug:
            font = pygame.font.SysFont(None, 18)
            text = f"{self.cx},{self.cy}"
            text_surface = font.render(text, True, (255, 255, 255))
            surf.blit(text_surface, (4, 4))
        self.surface_cache = surf
        return self.surface_cache

    def is_solid_at(self, x: int, y: int) -> bool:
        if 0 <= x < CHUNK_SIZE and 0 <= y < CHUNK_SIZE:
            tile_id = self.tiles[y, x]
            tile = TILEREG_TABLE.get(tile_id)
            return tile is not None and tile["solid"]
        return False

    @property
    def world_x(self):
        return self.cx * CHUNK_SIZE

    @property
    def world_y(self):
        return self.cy * CHUNK_SIZE
