# Project Management — Pac-Man

**Team:** ykhalouk, iandalou

---

## 1. Project Timeline

We used a simple Kanban board (Trello) with three columns: `To Do`, `In Progress`,
`Done`. Planned schedule over a 3-week window:

| Phase | Task | Owner | Planned start | Planned end |
|---|---|---|---|---|
| 1 | Read subject, split modules, agree on architecture | ykhalouk, iandalou | Day 1 | Day 1 |
| 1 | Config parser + JSON-with-comments loader | ykhalouk | Day 2 | Day 3 |
| 1 | Base widget system (`Widget`, `Playable`, `Controller`) | iandalou | Day 2 | Day 4 |
| 2 | A-Maze-ing package integration (`Canvas.generate`) | ykhalouk | Day 4 | Day 6 |
| 2 | Player movement + collisions | iandalou | Day 5 | Day 7 |
| 2 | Ghost AI (wander / chase / flee) | iandalou | Day 7 | Day 9 |
| 3 | Screens (menu, gameplay HUD, pause, instructions) | ykhalouk | Day 8 | Day 11 |
| 3 | Highscore system + save-score screen | iandalou | Day 10 | Day 12 |
| 3 | Cheat mode | ykhalouk | Day 12 | Day 13 |
| 4 | Lint (flake8/mypy), Makefile, packaging | ykhalouk, iandalou | Day 13 | Day 15 |
| 4 | README, project management docs, peer-review prep | ykhalouk, iandalou | Day 14 | Day 16 |


---

## 2. Actual Progress Tracking (vs. Timeline)

| Task | Planned end | Actual end | Notes on drift |
|---|---|---|---|
| Config parser | Day 3 | Day 3 | On time |
| Base widget system | Day 4 | Day 5 | Underestimated `VSelect`/`VContainer` padding & offset logic |
| A-Maze-ing integration | Day 6 | Day 8 | Assigned package's `maze` bitmask format wasn't documented; had to reverse-engineer it by testing wall rendering |
| Player movement | Day 7 | Day 7 | On time |
| Ghost AI | Day 9 | Day 11 | Initial random-wander ghosts were too easy; added BFS chase behavior, which took extra time |
| Screens | Day 11 | Day 12 | On time (small delay from ghost AI slipping) |
| Highscore system | Day 12 | Day 12 | On time |
| Cheat mode | Day 13 | Day 13 | On time |
| Lint/Makefile/packaging | Day 15 | Day 16 | mypy `--strict` surfaced several missing type hints, fixed late |
| README + docs | Day 16 | Day 16 | On time |

Overall: ~2 days behind the original plan, absorbed by compressing the packaging
phase and working in parallel during the last two days.

---

## 3. Project Analysis & Technical Choices

- **pygame over MLX**: chosen for better documentation, cross-platform support, and
  built-in joystick/audio handling, which simplified `Controller` and `Audio` in
  `src/helpers.py`.
- **Widget/Playable/Controller as separate mixins** (`src/helpers.py`) instead of one
  big base class: lets `Player`, `Ghost`, and `Reward` each opt into only the
  behaviors they need (e.g. `Reward` doesn't need `Controller`), keeping
  `objects.py` composable and easier to test in isolation.
- **Static `Configuration`/`Leaderboard` classes** (`src/parsing.py`) instead of
  passing a config object through every constructor: simplified wiring across
  screens at the cost of some testability, which we accepted given project scope.
- **JSON with `#`/`//` comment stripping** implemented as a manual line filter
  rather than a third-party JSON5 library: kept dependencies minimal, per the
  "robust error handling, no crash" requirement.
- **BFS shortest-path for ghost chase behavior** instead of A*: the maze is small
  enough (≤ ~20x15 cells) that BFS performance is a non-issue, and it's simpler to
  reason about and debug.

---

## 4. Risk Analysis & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Assigned A-Maze-ing package interface differs from what we expect | High | High | Wrote `Canvas.generate()` as a thin adapter around `MazeGenerator(...)`; isolated all maze-format assumptions inside `Canvas` so a change only touches one file |
| Config file crashes the game on bad input | Medium | High | Wrapped all `Configuration`/`Leaderboard` loading in `try/except`, raising a custom `ParsingException` caught once at the top level in `pac-man.py` |
| Ghost pathfinding tanking framerate on larger mazes | Low | Medium | Capped chase behavior to only trigger BFS when the player is within 6 cells; falls back to wander otherwise |
| Merge conflicts between the two of us working in `objects.py` and `screens.py` simultaneously | Medium | Medium | Split ownership by file per phase (see timeline) and communicated before touching shared files like `helpers.py` |
| Losing highscore data on crash mid-write | Low | Medium | `Utils.save()` writes the full file in one `write_text` call and creates parent dirs first, minimizing partial-write risk |

---

## 5. Team Organization

- **iandalou**: UI/widget system (`interface.py`, `screens.py`), player movement, ghost AI.
- **ykhalouk**: configuration & persistence (`parsing.py`), cheat mode, maze generator.
- Shared: `helpers.py` base classes, `playground.py` gameplay wiring, lint/Makefile,
  README and this document.
- **Decision making**: short daily syncs (15 min call); disagreements (e.g. BFS vs.
  simple distance-heuristic for ghosts) were resolved by prototyping both quickly and
  comparing playtest feel.
- **Issue handling**: bugs found during self-testing were logged as Trello cards with
  a screenshot/repro steps, assigned to whoever owned that module, and moved to
  `Done` once fixed and re-tested by the other partner.

---

## 6. Acceptance Test Plan

| Feature | Test | Expected result | Result | Bug found / fix |
|---|---|---|---|---|
| Config loading | Launch with valid JSON | Game starts with configured values | Pass | — |
| Config loading | Launch with missing file | Clear error message, no traceback | Pass | Initial version raised raw `FileNotFoundError`; wrapped in `ParsingException` |
| Config loading | Launch with malformed JSON | Clear error message, no traceback | Pass | — |
| Maze generation | Level 1 with fixed seed | Same maze every run | Pass | — |
| Maze generation | Level 2+ | Different maze each time | Pass | — |
| Player movement | Arrow keys / WASD | Player moves through corridors only | Pass | Diagonal "corner cutting" bug found, fixed by snapping to cell center before turning |
| Ghosts | Not scared, player nearby | Ghost moves toward player | Pass | — |
| Ghosts | After super-pacgum | Ghosts flee, become edible | Pass | — |
| Ghosts | Eaten while scared | Respawns at corner after cooldown | Pass | Respawn timing off by one animation frame; adjusted cooldown calc |
| Scoring | Eat pacgum / super-pacgum / ghost | Score increases by configured amount | Pass | — |
| Lives | Touched by non-scared ghost | Lose a life, respawn after freeze | Pass | — |
| Game over | Lives reach 0 | Save-score screen shown, then leaderboard | Pass | — |
| Win | All 10 levels cleared | Save-score screen shown with win message | Pass | — |
| Pause | Press `P` during gameplay | Game pauses, resume/menu options shown | Pass | — |
| Highscore | Save name + score | Persisted to JSON, shown in leaderboard sorted descending | Pass | Name length validation missing; added 10-char cap |
| Cheat mode | Keys `1`–`5` | Each toggles the matching cheat | Pass | — |

---

## 7. Blocking Points / Conflicts Summary

- **A-Maze-ing package format** was the single biggest blocker (see Risk table):
  cost ~2 extra days, resolved by isolating all maze-format handling inside `Canvas`.
- **No major interpersonal conflicts.** One design disagreement on ghost AI
  aggressiveness was resolved by playtesting both options together and picking the
  one that felt more fun/fair.
- Minor blocker: `mypy --strict` flagged several untyped `dict`/`Any` usages late in
  the project; resolved by tightening type hints across `helpers.py` and `objects.py`
  before submission.
