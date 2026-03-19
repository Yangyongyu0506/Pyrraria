from world.chunk import Chunk
from threading import Lock
from settings import (
    CHUNK_SIZE,
    TILE_SIZE,
)


class ChunkManager:
    def __init__(self, world, generator=None):
        """Manage loading/unloading of chunk data with optional generation."""
        self.world = world
        self.chunk_dict: dict[tuple[int, int], Chunk] = {}
        self.chunk_lock = Lock()
        self.generator = generator

    def get_chunk(self, cx, cy):
        """Return a loaded chunk by chunk coordinates if available."""
        with self.chunk_lock:
            return self.chunk_dict.get((cx, cy))

    def load_chunk(self, cx, cy):
        """Load a chunk from disk or generate it if missing."""
        chunk = Chunk(cx, cy)
        loaded = chunk.load(self.world.name)
        if not loaded and self.generator is not None:
            tiles = self.generator.gen_chunk(cx, cy)
            chunk.tiles = tiles
            chunk.dirty = True
        with self.chunk_lock:
            self.chunk_dict[(cx, cy)] = chunk
        return chunk

    def unload_chunk(self, cx, cy):
        """Persist and remove a chunk from memory."""
        with self.chunk_lock:
            if (cx, cy) in self.chunk_dict:
                chunk = self.chunk_dict[(cx, cy)]
                chunk.save(self.world.name)
                del self.chunk_dict[(cx, cy)]

    def set_tile_at(self, x, y, tile_id):
        """Set a tile at world-space coordinates, loading the chunk if needed."""
        cx = x // (CHUNK_SIZE * TILE_SIZE)
        cy = y // (CHUNK_SIZE * TILE_SIZE)
        chunk = self.get_chunk(cx, cy)
        if not chunk:
            chunk = self.load_chunk(cx, cy)
        local_x = x % (CHUNK_SIZE * TILE_SIZE) // TILE_SIZE
        local_y = y % (CHUNK_SIZE * TILE_SIZE) // TILE_SIZE
        chunk.set_tile(local_x, local_y, tile_id)

    def on_exit(self):
        """Persist all loaded chunks before shutdown."""
        with self.chunk_lock:
            for chunk in self.chunk_dict.values():
                chunk.save(self.world.name)
            self.chunk_dict.clear()

    def all_chunks(self):
        """Return a snapshot list of loaded chunk entries."""
        with self.chunk_lock:
            return list(self.chunk_dict.items())
