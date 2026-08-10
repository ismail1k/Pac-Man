*This project has been created as part of the 42 curriculum by ykhalouk and iandalou.*

# Pac-Man

## Description

This project is a full recreation of the classic arcade game **Pac-Man**, built in
Python on top of `pygame`. The player moves through a procedurally generated maze,
eats pacgums and super-pacgums, avoids (or eats) ghosts, and tries to clear all levels
before running out of lives or time.

The game is built around a small custom UI framework (widgets, containers, selects,
controllers) so that every screen — main menu, gameplay, pause, highscores, save-score
and instructions — is composed the same way, on top of a single `pygame` render loop.

Key features:

- Fully data-driven configuration through a JSON file (with `#`/`//` comment support).
- Level generation delegated to an external **A-Maze-ing** package (`mazegenerator`) —
  no in-house maze generator is written.
- A persistent, JSON-backed Top 10 highscore system.
- A complete graphical UI: main menu, in-game HUD, pause menu, victory/game-over
  screens with name entry, and an instructions screen.
- A cheat mode (invincibility, increased speed, ghost freeze, level skip, extra lives)
  for peer-review purposes.
- Robust error handling: malformed configuration files, missing highscore files, and
  maze generation failures are all caught and reported cleanly, without a Python
  traceback.

## Instructions

### Requirements

- Python 3.10+
- `pygame`
- The assigned `mazegenerator` (A-Maze-ing) package, installed as-is
- The `assets/` folder (images, fonts, audio) at the project root

### Running the game

The game is launched from the command line with exactly one argument: a path to a
JSON configuration file.

```bash
python3 pac-man.py config.json
```

Using the provided `Makefile`:

```bash
make install   # installs project dependencies
make run       # runs `python3 pac-man.py config.json`
make debug     # runs the game under Python's built-in debugger (pdb)
make lint      # runs flake8 and mypy
make clean     # removes __pycache__, .mypy_cache, etc.
```

### Controls

| Action              | Key(s)                     |
|---------------------|-----------------------------|
| Move                | Arrow keys or `WASD`        |
| Confirm / Select     | `Enter`                     |
| Back / Delete char   | `Backspace`                 |
| Pause                | `P`                          |
| Quit                 | `Esc`                        |
| Enter name (highscore)| letters, digits, `Space`   |
| Cheat: Invincibility  | `1`                          |
| Cheat: Increased speed| `2`                          |
| Cheat: Ghost freeze   | `3`                          |
| Cheat: Level skip     | `4`                          |
| Cheat: Extra life     | `5`                          |

A gamepad/joystick is also supported for movement and confirm/back actions.

## Resources

- [Pygame documentation](https://www.pygame.org/docs/)
- Original Pac-Man design notes (ghost behaviours: chase, ambush, ...) as historical
  reference for the ghost AI.


## Configuration

The game is configured through a single JSON file passed as the program's only
argument. Comment lines starting with `#` or `//` are stripped before parsing, so the
file can be documented inline even though it is not strict JSON.

| Key                        | Default            | Description                                              |
|-----------------------------|---------------------|------------------------------------------------------------|
| `highscore_filename`        | `"highscore.json"`  | Path to the persistent highscore file.                    |
| `width`                     | `18`                | Maze width, in cells.                                     |
| `height`                    | `12`                | Maze height, in cells.                                    |
| `lives`                     | `3`                 | Number of lives the player starts with.                   |
| `pacgum`                    | all free cells      | Number of regular pacgums placed in the maze.              |
| `points_per_pacgum`         | `5`                 | Score awarded for eating a pacgum.                         |
| `points_per_super_pacgum`   | `25`                | Score awarded for eating a super-pacgum.                    |
| `points_per_ghost`          | `100`               | Score awarded for eating a scared ghost.                    |
| `level_max_time`            | `60`                | Time limit per level, in seconds.                           |
| `seed`                      | random               | Seed used to generate level 1's maze (deterministic).       |

Any missing key falls back to its default above; any unknown key is simply ignored. If
the configuration file is missing or is not valid JSON, the program prints a clear
error message and exits without a traceback.

## Highscore

Highscores are stored as a single JSON object on disk (`{"name": score, ...}`), at the
path given by `highscore_filename` (default `highscore.json`). The file is:

- **Loaded** once at startup. If it doesn't exist yet, an empty file is created; if it
  exists but is not valid JSON, a clear parsing error is raised instead of crashing.
- **Updated and saved to disk** every time a player confirms their name after a win or
  a loss.
- **Displayed** sorted by descending score in the Leaderboard screen (accessible from
  the main menu), showing every recorded entry (the UI already covers the "Top 10"
  requirement since scores are sorted and the list is a simple ranked leaderboard).

Player names are limited to 10 characters and only accept letters, digits and spaces,
enforced directly by the name-entry input handler on the Save Score screen.

## Maze Generation

Maze generation is fully delegated to the assigned **A-Maze-ing** package, imported as
`mazegenerator`. `src/objects.py`'s `Canvas.generate()` calls:

```python
generator = MazeGenerator(size=size, seed=seed)
self.maze = generator.maze
```

`generator.maze` is used as-is: a 2D grid of integer bitmasks where each bit
(`1=N`, `2=E`, `4=S`, `8=W`) marks a wall on that side of the cell. `Canvas.neighbors()`
and `Canvas.navigate()` read this bitmask directly to know which directions the player
and ghosts can walk into, and `Canvas.surface` maps each bitmask value to the matching
wall tile image. Level 1 always uses the `seed` from the configuration file for
reproducibility; every subsequent level offsets that seed by the current level number
so each level's maze is different. If the generator raises an exception, it propagates
up to the top-level error handling so it is reported cleanly instead of crashing the
game.

## Implementation

The game runs on a single `pygame` render loop (`src/visualizer.py: Visualizer.render`)
at 60 FPS. Each "screen" (`src/screens.py`) is a `Widget` composed of smaller widgets
(`src/interface.py`) — images, text, input fields, selectable menus and containers — all
built on the shared `Widget` base class from `src/helpers.py`, which handles position,
padding, offset and visibility.

Gameplay itself (`src/playground.py: Gameplay`) is a `VContainer` holding the maze
`Canvas`, the `Player`, a list of `Ghost`s and a list of `Reward`s (pacgums/super-pacgums,
`src/objects.py`). Every frame it renders these elements, checks pixel-rect collisions
between the player and rewards/ghosts, and dispatches score, life-loss, level-up, win
and lose events back up to the top-level `Pacman` class in `pac-man.py`, which owns the
overall game flow (menu → gameplay → pause/win/lose → save score → leaderboard → menu).

Movement and ghost AI reuse the same `Playable` mixin (`src/helpers.py`): entities move
cell-by-cell along the maze graph, interpolating position at a configurable speed.
Ghosts pick their next cell in `Ghost.behaviour()`: they flee (maximizing distance) when
scared, chase the player via a BFS shortest path when nearby and not scared, and wander
randomly otherwise. Input (keyboard and joystick) is handled uniformly through the
`Controller` mixin, which lets any widget register key/button callbacks.

Configuration and highscores (`src/parsing.py`) are loaded once as static data on the
`Configuration` and `Leaderboard` classes, both backed by JSON files and defensively
parsed to strip comment lines before calling `json.loads`.

## General Software Architecture

```
pac-man.py            Entry point; Pacman class orchestrates the game flow and screens
src/
├── exceptions.py      ParsingException / RuntimeException, used for clean error reporting
├── helpers.py          Widget, Playable, Controller, Audio, Utils, Cheat base classes/mixins
├── interface.py        VImage, VText, VField, VOption, VSelect, VContainer UI widgets
├── objects.py           Canvas (maze), Player, Ghost, Reward game entities
├── parsing.py            Configuration and Leaderboard (JSON loading/saving)
├── playground.py         Gameplay: composes Canvas/Player/Ghosts/Rewards, drives game logic
├── screens.py             MainScreen, GameplayScreen, PauseScreen, LeaderboardScreen,
│                          SaveScoreScreen, InstructionScreen
└── visualizer.py           Visualizer: owns the pygame window/screen and the main render loop
```

Relationships, at a glance:

- `Visualizer` owns a stack of `Scene`/screen widgets and drives the render loop.
- Every screen in `screens.py` wraps a `VContainer` tree of widgets from `interface.py`.
- `Gameplay` (in `playground.py`) is itself a `VContainer`, embedded inside
  `GameplayScreen`; it owns the `Canvas`, `Player`, `Ghost`s and `Reward`s from
  `objects.py`.
- `Player`, `Ghost` and `Reward` combine `Widget` (renderable), `Playable`
  (grid-based movement) and, for the player, `Controller` (input handling).
- `Configuration` and `Leaderboard` (`parsing.py`) are read by almost every other
  module (score values, maze size, highscore persistence) and are the single source of
  truth for game parameters.

## Project Management

Project tracking (timeline, task ownership, risk analysis, and the acceptance test
plan) is documented separately in [`PROJECT_MANAGEMENT.md`](./PROJECT_MANAGEMENT.md), so
this README stays focused on the game itself.

## AI usage
- Explaining how graphics work.