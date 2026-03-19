# Pyrraria
Pyrraria is a Python parody of the renowned 2D sandbox game Terraria. It is a pygame-based prototype that focuses on chunked world rendering, basic tile interactions, and a lightweight entity system.

## Highlights
- Chunked, wraparound world with background rendering
- Rich tile registry (sand, water, clay, snow, ice, gravel)
- Large, continuous cavern generation
- Background chunk IO thread with streaming loads/unloads
- Player entity with gravity, jump, collision, and fall damage

## Requirements
- Python 3.12+
- Dependencies: `pygame`, `numpy`, `noise`

## Quick start
1. Create and activate a virtual environment.
2. Install dependencies.
3. Run the game.
4. Press Alt+F4 to exit the game.

```bash
pip install -r requirements.txt
python main.py
```

If you use `uv`, install from `pyproject.toml` and `uv.lock` instead:

```bash
uv sync
python main.py
```

## Controls
- `A`, `D`: move the player
- `W` or `Space`: jump
- Left mouse button: set the clicked tile to air (remove)
- Window close: quit and save chunks

## Project structure
- `main.py`: entry point
- `core/`: game loop, camera, input
- `world/`: chunks, world management, terrain generation
- `entities/`: entity base classes and hitboxes
- `assets/`: background and art assets
- `user/world_data/`: generated and saved chunk data

## Notes
- Terrain generation lives in `world/generator.py`, but the runtime world loads chunk files on demand. If a chunk file does not exist yet, it starts empty.
- Player input is driven by `InputManager`'s `InputFrame`, and the camera follows the player.
- Logs include chunk load/unload events and player position (throttled).
- Player fall damage triggers on hard landings.
- World size and tuning constants are in `settings.py`.

## Roadmap ideas
- Hook up procedural generation for missing chunks
- Expand player tools and inventory
- Tile breaking and placement with inventory
- More biome variety and decorations

## License
See `LICENSE`.
