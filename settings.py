from pathlib import Path

TILE_SIZE = 16
CHUNK_LOAD_RADIUS = 7
FPS = 60
CHUNK_SIZE = 32
WORLD_CHUNK_WIDTH = 64
WORLD_CHUNK_HEIGHT = 32
DIR_ROOT = str(Path(__file__).resolve().parent)

MAX_ENTITIES = 200
ACC_G = TILE_SIZE * 10.0  # gravity acceleration in pixels/s^2
