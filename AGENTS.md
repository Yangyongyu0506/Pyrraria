# AGENTS.md

This file guides agentic coding assistants working in this repository.
Use it as the default source for build, test, lint, and style behavior.

If unsure, copy existing patterns in `core/`, `world/`, `entities/`,
`systems/`, `ui/`, and `utils/`.

Cursor rules status
- No rules found in `.cursor/rules/`.
- No `.cursorrules` file found.

Copilot rules status
- No `.github/copilot-instructions.md` file found.

---------------------------------------------------------------------
Build / Run / Test / Lint
---------------------------------------------------------------------

Runtime
- Python `>=3.12` (from `pyproject.toml`).
- Dependencies: `pygame`, `numpy`, `noise`.

Install dependencies
- With `uv` (preferred if available):
  - `uv sync`
- With `pip` (README flow):
  - `pip install -r requirements.txt`
  - Note: `requirements.txt` may be absent in some clones.

Run application
- Start game: `python main.py`
- One-off world generation script: `python test.py`

Tests
- There is currently no configured test suite in this repo.
- If tests are added, use `pytest` conventions:
  - Run all tests: `python -m pytest`
  - Run one file: `python -m pytest tests/test_file.py`
  - Run one test function: `python -m pytest tests/test_file.py::test_name`
  - Run one test method:
    `python -m pytest tests/test_file.py::TestClass::test_name`
  - Useful flags while iterating: `-q`, `-x`, `-k <expr>`

Lint / format / type check
- No formatter, linter, or type-checker is configured today.
- Do not introduce a new toolchain unless explicitly requested.
- If tooling is added later, document exact commands here.

---------------------------------------------------------------------
Repository Map
---------------------------------------------------------------------

- `main.py`: game entrypoint (`Game` creation + `run`).
- `core/`: loop orchestration, camera, input framing.
- `world/`: chunk storage/streaming, generation, tile registry, tools.
- `entities/`: base entity logic, player, drops, collision manager.
- `systems/`: input, digging, placement, pickup, discard, physics.
- `ui/`: HUD, inventory, backpack rendering and interaction.
- `utils/`: math helpers and coordinate conversions.
- `settings.py`: gameplay and world constants.

---------------------------------------------------------------------
Code Style Guidelines
---------------------------------------------------------------------

General
- Prefer straightforward, explicit code over abstraction-heavy designs.
- Keep functions focused; extract helpers once logic becomes long/noisy.
- Keep game rules in systems; keep entities mostly stateful.
- Make side effects obvious (disk I/O, pygame draws, logging, threads).

Formatting
- Use 4-space indentation.
- Keep lines reasonably short; break long calls with parentheses.
- Use trailing commas in multiline literals/calls.
- Avoid broad rewrites that only change formatting.

Imports
- Group imports: stdlib, third-party, local modules.
- Use absolute imports rooted at project packages.
- Avoid relative imports unless a module already uses them.
- Prefer explicit imports over wildcard imports.

Typing
- Use Python 3.12 type hints for public and cross-module APIs first.
- Prefer built-in generic syntax (`list[int]`, `dict[str, int]`).
- Use `X | None` instead of `Optional[X]`.
- Add/keep return types where behavior is not obvious.

Naming
- Modules/files: `snake_case.py`.
- Classes: `PascalCase`.
- Functions, methods, variables: `snake_case`.
- Constants: `UPPER_SNAKE_CASE` (see `settings.py`).
- Keep names domain-oriented (`chunk`, `tile`, `spawn`, `hitbox`, etc.).

Docstrings and comments
- Use concise triple-quoted docstrings on classes/methods.
- Prefer behavior-focused docs over parameter dumps.
- Add comments only for non-obvious intent or invariants.

Error handling
- Catch narrow exceptions (`FileNotFoundError`, `ValueError`, etc.).
- Prefer safe fallbacks for recoverable runtime issues.
- Do not silently swallow errors unless fallback is intentional.
- Use logging for operational issues; avoid `print` in runtime paths.

Logging
- Reuse module/game loggers (e.g., `logging.getLogger("pyrraria.*")`).
- Keep logging low-noise inside per-frame or per-tile loops.
- Log state transitions and failures, not every update tick.

Data persistence
- World/chunk saves live under `user/world_data/<world>/`.
- Player inventory/backpack lives under `user/player/`.
- Reuse existing save/load helpers before adding new file formats.

Pygame and performance
- Use `pygame.Surface`/`pygame.Rect` consistently.
- Avoid heavy allocations in hot paths (update/render loops).
- Cache transformed/scaled assets when screen size is unchanged.
- Keep render/update deterministic unless randomness is intentional.

World and coordinates
- World coordinates are pixel-based; tile size comes from `settings.py`.
- Camera origin is top-left in screen space.
- Use helpers in `utils/maths.py` for conversions and interpolation.
- Preserve world wrapping behavior when editing chunk/tile logic.

Collision and physics
- Position integration is handled in entity update methods.
- Collision resolution is centralized in `EntityManager`.
- Keep physics deterministic and frame-rate aware (`dt` based updates).

Systems architecture
- Route input effects through systems (`DigSystem`, `PickupSystem`, etc.).
- Avoid embedding new gameplay rules directly in `Player` when avoidable.
- Keep system APIs narrow and composable from the main game loop.

Concurrency and I/O
- Chunk streaming uses a background thread in `World.chunk_io`.
- Guard shared chunk state with existing locking strategy.
- Avoid blocking operations on the main thread.

---------------------------------------------------------------------
Agent Workflow Notes
---------------------------------------------------------------------

- Make minimal, targeted changes; avoid unrelated refactors.
- Preserve backward-compatible behavior unless asked otherwise.
- When adding tests, prefer deterministic unit tests under `tests/`.
- If you add tooling (pytest/ruff/mypy/etc.), update this file.
