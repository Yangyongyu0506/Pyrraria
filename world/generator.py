import numpy as np
import os
from noise import pnoise1, pnoise2

from settings import CHUNK_SIZE, WORLD_CHUNK_WIDTH, WORLD_CHUNK_HEIGHT, DIR_ROOT

AIR = 0
DIRT = 1
STONE = 2
GRASS = 3
ORE = 4
SAND = 5
WATER = 6
CLAY = 7
SNOW = 8
ICE = 9
GRAVEL = 10


class Generator:
    def __init__(self, seed=42, world_name="new_world"):
        """Procedural terrain generator for chunks and world metadata."""

        self.seed = seed
        self.world_name = world_name

        self.WORLD_TILE_WIDTH = WORLD_CHUNK_WIDTH * CHUNK_SIZE
        self.WORLD_TILE_HEIGHT = WORLD_CHUNK_HEIGHT * CHUNK_SIZE

        os.makedirs(f"{DIR_ROOT}/user/world_data/{world_name}", exist_ok=True)

    # ------------------------
    # heightmap
    # ------------------------

    def get_height(self, x):
        """Return surface height at a given world x coordinate."""

        large = pnoise1(x * 0.003, repeat=self.WORLD_TILE_WIDTH, base=self.seed)

        small = pnoise1(x * 0.02, repeat=self.WORLD_TILE_WIDTH, base=self.seed + 1)

        BASE_HEIGHT = 60

        height = BASE_HEIGHT + large * 25 + small * 6

        return int(height)

    def get_biome_value(self, x):
        """Return a low-frequency biome noise value at x."""

        return pnoise1(x * 0.001, repeat=self.WORLD_TILE_WIDTH, base=self.seed + 300)

    def get_moisture(self, x):
        """Return a moisture noise value at x."""

        return pnoise1(x * 0.002, repeat=self.WORLD_TILE_WIDTH, base=self.seed + 400)

    # ------------------------
    # cave system
    # ------------------------

    def is_cave(self, x, y):
        """Return True if the tile should be carved into a cave."""

        base = pnoise2(
            x * 0.010,
            y * 0.010,
            octaves=1,
            persistence=0.5,
            lacunarity=2.0,
            repeatx=self.WORLD_TILE_WIDTH,
            repeaty=self.WORLD_TILE_HEIGHT,
            base=self.seed + 100,
        )

        detail = pnoise2(
            x * 0.035,
            y * 0.035,
            octaves=2,
            persistence=0.6,
            lacunarity=2.0,
            repeatx=self.WORLD_TILE_WIDTH,
            repeaty=self.WORLD_TILE_HEIGHT,
            base=self.seed + 101,
        )

        carve = base * 0.85 + detail * 0.35

        return carve > 0.18

    # ------------------------
    # ore veins
    # ------------------------

    def is_ore(self, x, y):
        """Return True if a tile should become ore."""

        ore = pnoise2(
            x * 0.07,
            y * 0.07,
            repeatx=self.WORLD_TILE_WIDTH,
            repeaty=self.WORLD_TILE_HEIGHT,
            base=self.seed + 200,
        )

        return ore > 0.63

    def is_gravel(self, x, y):
        """Return True if a tile should become gravel."""

        gravel = pnoise2(
            x * 0.09,
            y * 0.09,
            repeatx=self.WORLD_TILE_WIDTH,
            repeaty=self.WORLD_TILE_HEIGHT,
            base=self.seed + 220,
        )

        return gravel > 0.68

    def is_clay(self, x, y):
        """Return True if a tile should become clay."""

        clay = pnoise2(
            x * 0.06,
            y * 0.06,
            repeatx=self.WORLD_TILE_WIDTH,
            repeaty=self.WORLD_TILE_HEIGHT,
            base=self.seed + 230,
        )

        return clay > 0.66

    # ------------------------
    # base terrain
    # ------------------------

    def base_terrain(self, wx, wy, surface):
        """Return the base material for a given world position."""

        if wy < surface:
            return AIR

        if wy == surface:
            return GRASS

        if wy < surface + 4:
            return DIRT

        return STONE

    def surface_tile(self, wx, wy, surface):
        """Pick a surface material based on biome and moisture."""

        biome = self.get_biome_value(wx)
        moisture = self.get_moisture(wx)

        if biome > 0.35:
            return SNOW
        if biome < -0.35:
            return SAND
        if moisture > 0.35:
            return GRASS

        return GRASS

    # ------------------------
    # chunk generation
    # ------------------------

    def gen_chunk(self, cx, cy):
        """Generate a chunk's tile grid from procedural rules."""

        tiles = np.zeros((CHUNK_SIZE, CHUNK_SIZE), dtype=np.uint8)

        for y in range(CHUNK_SIZE):
            for x in range(CHUNK_SIZE):
                wx = cx * CHUNK_SIZE + x
                wy = cy * CHUNK_SIZE + y

                surface = self.get_height(wx)

                tile = self.base_terrain(wx, wy, surface)

                if wy == surface:
                    tile = self.surface_tile(wx, wy, surface)

                if tile == DIRT and wy < surface + 6:
                    biome = self.get_biome_value(wx)
                    if biome > 0.35:
                        tile = SNOW
                    elif biome < -0.35:
                        tile = SAND

                # caves
                if tile in (
                    STONE,
                    DIRT,
                    GRASS,
                    SAND,
                    CLAY,
                    SNOW,
                    ICE,
                    GRAVEL,
                ) and self.is_cave(wx, wy):
                    tile = AIR

                # ores and materials
                if tile == STONE and self.is_ore(wx, wy):
                    tile = ORE
                elif tile == STONE and self.is_gravel(wx, wy):
                    tile = GRAVEL
                elif tile == DIRT and self.is_clay(wx, wy):
                    tile = CLAY

                # underground water pockets
                if tile == AIR and wy > surface + 8:
                    moisture = self.get_moisture(wx)
                    if moisture > 0.45:
                        tile = WATER

                tiles[y, x] = tile

        return tiles

    # ------------------------
    # save chunk
    # ------------------------

    def write_chunk(self, cx, cy, tiles):
        """Write chunk tiles to disk."""

        path = f"{DIR_ROOT}/user/world_data/{self.world_name}/chunk_{cx}_{cy}.npy"

        np.save(path, tiles)

    # ------------------------
    # generate world
    # ------------------------

    def generate_world(self):
        """Generate and persist the full world plus spawn metadata."""

        for cy in range(WORLD_CHUNK_HEIGHT):
            for cx in range(WORLD_CHUNK_WIDTH):
                tiles = self.gen_chunk(cx, cy)
                self.write_chunk(cx, cy, tiles)
        # write a file that caches the spawn point height
        spawn_x = self.WORLD_TILE_WIDTH // 2
        spawn_y = self.get_height(spawn_x)
        with open(
            f"{DIR_ROOT}/user/world_data/{self.world_name}/spawn_point.txt", "w"
        ) as f:
            f.write(f"{spawn_x},{spawn_y - 2}")
