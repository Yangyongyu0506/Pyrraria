# AGENTS.md

This guide is for agentic coding assistants working in this repo.
It summarizes how to build/run, how to lint/test, and the code style
conventions used across the project.

If you are unsure, follow existing patterns in the files under
`core/`, `world/`, `entities/`, `systems/`, `ui/`, and `utils/`.

Cursor rules: none found in `.cursor/rules/` or `.cursorrules`.
Copilot rules: none found in `.github/copilot-instructions.md`.

---------------------------------------------------------------------
Build / Run / Lint / Test
---------------------------------------------------------------------

Runtime
- Python 3.12+ (see `pyproject.toml`).
- Dependencies: `pygame`, `numpy`, `noise`.

Install dependencies (venv)
- If you use `pip`:
  - `pip install -r requirements.txt` (mentioned in README, file may
    be missing in some clones; confirm before relying on it).
- If you use `uv`:
  - `uv sync`

Run the game
- `python main.py`

One-off world generation
- `python test.py`

Tests
- There is no configured test runner in this repository.
- If you add pytest later, common usage is:
  - `python -m pytest`
  - Single test file: `python -m pytest path/to/test_file.py`
  - Single test: `python -m pytest path/to/test_file.py::TestClass::test_name`

Linting / Formatting / Type checking
- No configured lint or format tool (no ruff/black/flake8/mypy found).
- If you add one, document it here and keep it consistent with existing
  patterns (see Style Guide below).

---------------------------------------------------------------------
Project Structure
---------------------------------------------------------------------

- `main.py`: entry point (create `Game`, call `run()`).
- `core/`: game loop, camera, input.
- `world/`: chunk streaming, terrain generation, tile registry.
- `entities/`: entities, collision, player logic.
- `systems/`: input, digging, placement, pickup, physics, discard.
- `ui/`: health bar, inventory HUD.
- `utils/`: small math helpers.
- `settings.py`: shared constants.

---------------------------------------------------------------------
Style Guide (follow existing patterns)
---------------------------------------------------------------------

General
- Prefer clear, simple logic over clever abstractions.
- Keep functions short; use helpers when blocks grow large.
- Use docstrings for classes and methods; most functions already have
  one-line summaries.
- Keep side effects explicit (I/O, pygame calls, file writes).

Formatting
- 4-space indents.
- Keep lines reasonably short; wrap long calls with parentheses.
- Use trailing commas when multi-line argument lists are present.
- Avoid adding unnecessary comments; use docstrings instead.

Imports
- Standard library first, third-party next, local imports last.
- Use explicit module imports (e.g. `from world.world import World`).
- Prefer absolute imports rooted at repo modules (no relative imports).
- Group imports with a blank line between groups when mixing types.

Types
- Use Python 3.12 type hints; prefer built-in generics:
  - `list[Type]`, `dict[Key, Value]`, `tuple[int, int]`.
- Use `X | None` for optional types.
- Add types to public APIs and cross-module boundaries first.

Naming
- Modules/files: `snake_case.py`.
- Classes: `PascalCase` (e.g. `EntityManager`).
- Functions/variables: `snake_case`.
- Constants: `UPPER_SNAKE_CASE` (see `settings.py`).

Docstrings
- Use triple-quoted, short summaries on classes and methods.
- Focus on behavior and side effects rather than parameters only.

Error Handling
- Use narrow exceptions (e.g., `FileNotFoundError`, `ValueError`).
- Prefer returning safe defaults rather than crashing (see
  `World.load_spawn_point`).
- If you must log, use the module or injected logger, not `print`.

Logging
- The game loop configures logging in `Game.__init__`.
- Use `logging.getLogger("pyrraria.<area>")` where needed.
- Avoid noisy logs in tight loops; log on state changes only.

Data and Persistence
- World chunks are stored under `user/world_data/<world>/`.
- Inventory saves to `user/player/inventory.json`.
- Backpack saves to `user/player/backpack.json`.
- Prefer existing save/load helpers in `Chunk` and `Inventory`.

Systems
- Use systems to own game logic (digging, pickup, placement, input).
- Keep `Player` focused on state; avoid embedding new game rules there.
- Route tool checks and tile breaking through `DigSystem`.

Concurrency
- Chunk streaming uses a background thread (`World.chunk_io`).
- Protect shared state using locks (see `ChunkManager.chunk_lock`).
- Avoid blocking the main thread with I/O.

Coordinate Systems
- World space uses pixels; tile size in `settings.py`.
- Camera origin is the top-left of the screen.
- Use helpers in `utils/maths.py` for conversions.

Physics and Collision
- Entities update positions in `Entity.update_pos`.
- Collisions are resolved in `EntityManager.solve_collisions`.
- Keep collision logic deterministic; avoid random in core physics.

Pygame Usage
- Use `pygame.Surface` and `pygame.Rect` consistently.
- Convert surfaces when needed (see `Chunk.surface`).
- Avoid expensive per-frame allocations where possible.

Tiles
- Tile metadata is in `world/tilereg.py`.
- Use tile IDs consistently (0 is air).
- When adding tiles, update `TILEREG_TABLE` and `TILE_DROPS`.

Items and Tools
- Item registry lives in `entities/itemreg.py`.
- Tools are defined in `world/tools.py` and are unstackable.
- Digging requires a tool with `can_dig`.

UI
- UI classes live in `ui/` and are lightweight.
- Rendering uses simple primitives; keep HUD fast.
- Backpack UI toggles with `E`; use `h/j/k/l` for cursor and `1-9` to swap with hotbar.

Testing Additions (if you add tests)
- Prefer pytest; organize under `tests/`.
- Keep tests deterministic; avoid real-time waits.
- Add a single-test command in this file when tests exist.

---------------------------------------------------------------------
Common Tasks
---------------------------------------------------------------------

- Run game: `python main.py`
- Generate world (dev): `python test.py`
- Adjust constants: edit `settings.py`

---------------------------------------------------------------------
Agent Notes
---------------------------------------------------------------------

- Do not introduce a new toolchain unless requested.
- Respect existing patterns; this is a small prototype codebase.
- If you add linting or tests, update this file accordingly.
