"""Game entities and maze canvas used by the game."""

import pygame
import random
import os
from time import time
from typing import Any
from mazegenerator import MazeGenerator
from src.parsing import Configuration
from src.visualizer import Visualizer
from src.helpers import Widget, Playable, Controller, Cheat


class Reward(Widget, Playable):
    """Represents a collectible reward in the game."""

    textures: list[str] = [
        "assets/images/point.png",
        "assets/images/coin_special.png",
    ]

    def __init__(
        self,
        canvas: Any,
        states: dict = {},
        special: bool = False
    ) -> None:
        """Initialize a reward with its canvas, state, and special type."""
        size: tuple = (30, 30) if special else (15, 15)
        texture: str = self.textures[1 if special else 0]
        surface = pygame.image.load(texture).convert_alpha()
        Widget.__init__(self, pygame.transform.smoothscale(surface, size))
        Playable.__init__(self, canvas, states)
        self.special: bool = special
        self.padding.update({
            'left': 15 if self.special else 22,
            'bottom': 15 if self.special else 22,
            'right': 15 if self.special else 22,
            'top': 15 if self.special else 22
        })


class Player(Widget, Playable, Controller):
    """Represents the player character and handles player input."""

    textures: list[str] = [
        "assets/images/player_close.png",
        "assets/images/player_open.png",
    ]

    def __init__(self, canvas: Any, states: dict = {}) -> None:
        """Initialize the player with movement and controller handling."""
        Widget.__init__(self, pygame.Surface((0, 0)))
        Playable.__init__(self, canvas, states)
        Controller.__init__(self)
        self.onClick(
            self.ACTION_UP,
            lambda: self._cache.update({'direction': "N"})
        )
        self.onClick(
            self.ACTION_DOWN,
            lambda: self._cache.update({'direction': "S"})
        )
        self.onClick(
            self.ACTION_LEFT,
            lambda: self._cache.update({'direction': "W"})
        )
        self.onClick(
            self.ACTION_RIGHT,
            lambda: self._cache.update({'direction': "E"})
        )

        # this clicks for the cheat mode
        self.onClick([pygame.K_1], Cheat.set_invincibility)
        self.onClick([pygame.K_2], Cheat.set_increased_speed)
        self.onClick([pygame.K_3], Cheat.set_ghost_freeze)
        self.onClick([pygame.K_4], Cheat.set_level)
        self.onClick([pygame.K_5], Cheat.set_extra_lives)

        self.padding.update({'left': 15, 'bottom': 15, 'right': 15, 'top': 15})
        self.speed: float = 8.0

        self.surface0 = pygame.image.load(self.textures[0]).convert_alpha()
        self.surface1 = pygame.image.load(self.textures[1]).convert_alpha()

    @property
    def surface(self) -> pygame.Surface:
        """Return the player's surface based on its direction and state."""
        mouth: int = 0
        angle: int = 0
        flip: bool = False
        if self.direction == 'E':
            mouth = 1
            angle = 0
        elif self.direction == 'N':
            mouth = 1
            angle = 90
        elif self.direction == 'W':
            mouth = 1
            angle = 180
            flip = True
        elif self.direction == 'S':
            mouth = 1
            angle = 270

        if mouth == 0:
            surface = self.surface0
        else:
            surface = self.surface1

        surface = pygame.transform.smoothscale(surface, (35, 35))
        surface = pygame.transform.flip(surface, False, flip)
        if Cheat.invincibility:
            surface.set_alpha(128)
        return pygame.transform.rotate(surface, angle)

    @surface.setter
    def surface(self, surface: pygame.Surface) -> None:
        """Set the widget surface and update its dimensions."""
        self.width, self.height = surface.get_size()
        self._surface = surface

    def onDestroy(self) -> None:
        """Remove all controller events associated with the player."""
        self.destroyControllerEvents()

    def render(self, visual: Visualizer) -> None:
        """Update the player and render it on the visualizer."""
        if Cheat.increased_speed:
            self.speed = 4.0
        else:
            self.speed = 2.0
        self.listenControllerEvents(visual.events)
        self.thread()
        if self.visible:
            visual.screen.blit(self.surface, self.position)


class Ghost(Widget, Playable):
    """Represents a ghost that moves through and reacts to the maze."""

    textures: list[str] = [
        "assets/images/ghost_blue.png",
        "assets/images/ghost_green.png",
        "assets/images/ghost_pink.png",
        "assets/images/ghost_red.png",
        "assets/images/enemy_fear_white.png",
    ]

    def __init__(self, canvas: Any, states: dict = {}) -> None:
        """Initialize the ghost with its canvas and movement state."""
        Widget.__init__(self, pygame.Surface((0, 0)))
        Playable.__init__(self, canvas, states)
        self.player: Player | None = None
        self.scared_at: float = 0.0
        self.init_cell: tuple[int, int] = (0, 0)
        self.padding.update({'left': 15, 'bottom': 15, 'right': 15, 'top': 15})
        self.type: int = 0
        self.invincibility: bool = Configuration.get("invincibility", False)

    @property
    def surface(self) -> pygame.Surface:
        """Return the ghost's current surface based on its state."""
        surface = pygame.image.load(self.textures[self.type]).convert_alpha()
        if self.scared_at + 15 > time():
            cooldown = int(abs(time() - self.scared_at - 15))
            surface = pygame.image.load(self.textures[-1]).convert_alpha()
            if cooldown <= 5:
                if cooldown % 2 == 0:
                    surface = pygame.image.load(
                        self.textures[self.type]).convert_alpha()
        return pygame.transform.smoothscale(surface, (35, 35))

    @surface.setter
    def surface(self, surface: pygame.Surface) -> None:
        """Set the widget surface and update its dimensions."""
        self.width, self.height = surface.get_size()
        self._surface = surface

    def behaviour(self) -> None:
        """Determine the ghost's next movement direction."""
        if Cheat.ghost_freeze:
            self._cache["direction"] = ""
            return

        def reverse(direction: str) -> str:
            """Return the opposite direction."""
            if direction == 'N':
                return 'S'
            if direction == 'S':
                return 'N'
            if direction == 'E':
                return 'W'
            if direction == 'W':
                return 'E'
            return ''

        def wander() -> None:
            """Choose a random valid direction for wandering."""
            neighbors = self.canvas.neighbors(self.cell)
            if self.direction:
                rev = reverse(self.direction)
                choices = [d for d in neighbors if d != rev]
            else:
                choices = neighbors

            if choices:
                self._cache["direction"] = random.choice(choices)
            elif self.direction:
                self._cache["direction"] = reverse(self.direction)
            else:
                self._cache["direction"] = ""

        player: Player | None = self.player
        if player is None or not player.visible:
            return wander()

        scared: bool = self.scared_at + 15 > time()
        distance: int = abs(
            self.cell[0] - player.cell[0]
        ) + abs(
            self.cell[1] - player.cell[1]
        )

        if scared:
            neighbors = self.canvas.neighbors(self.cell)
            if self.direction:
                rev = reverse(self.direction)
                candidates = [d for d in neighbors if d != rev] or neighbors
            else:
                candidates = neighbors

            best_direction: str = ""
            best_distance: int = -1
            for direction in candidates:
                target = self.canvas.navigate(self.cell, direction)
                if target is None:
                    continue
                target_distance = abs(
                    target[0] - player.cell[0]
                ) + abs(
                    target[1] - player.cell[1]
                )
                if target_distance > best_distance:
                    best_distance = target_distance
                    best_direction = direction
            self._cache["direction"] = best_direction
            return

        if distance <= 6 and not Cheat.invincibility:
            path = self._find_path(self.cell, player.cell)
            if path and len(path) > 1:
                dx = path[1][0] - self.cell[0]
                dy = path[1][1] - self.cell[1]
                direction = {
                    (0, -1): 'N',
                    (1, 0): 'E',
                    (0, 1): 'S',
                    (-1, 0): 'W'
                }.get((dx, dy), '')
                if direction:
                    self._cache["direction"] = direction
                    return

        wander()

    def _find_path(
        self,
        start: tuple[int, int],
        goal: tuple[int, int]
    ) -> list[tuple[int, int]] | None:
        """Find a path between two cells using breadth-first search."""
        from collections import deque
        if start == goal:
            return [start]
        visited: set = {start}
        queue = deque([[start]])
        while queue:
            path = queue.popleft()
            current = path[-1]
            for direction in self.canvas.neighbors(current):
                next_cell = self.canvas.navigate(current, direction)
                if next_cell is None or next_cell in visited:
                    continue
                new_path = path + [next_cell]
                if next_cell == goal:
                    return new_path
                visited.add(next_cell)
                queue.append(new_path)
        return None

    def render(self, visual: Visualizer) -> None:
        """Update the ghost and render it on the visualizer."""
        self.thread()
        if self.visible:
            visual.screen.blit(self.surface, self.position)


class Canvas(Widget):
    """Represents and renders the maze used by the game."""

    thickness = 5
    cell_size: int = 60

    def __init__(self) -> None:
        """Initialize an empty maze canvas."""
        super().__init__(pygame.Surface((0, 0)))
        self.maze: list[list[int]] = []

    @property
    def surface(self) -> pygame.Surface:
        """Render and return the maze surface."""
        maze = self.maze
        cell_size = self.cell_size
        tile_dir = "assets/images"
        rows = len(maze)
        cols = len(maze[0])
        tile_map = {
            0x1: "wall_I_top.png",
            0x2: "wall_I_right.png",
            0x4: "wall_I_down.png",
            0x8: "wall_I_left.png",
            0x5: "wall_horizontal.png",
            0xA: "wall_vertical.png",
            0x9: "wall_L_top_left.png",
            0x3: "wall_L_top_right.png",
            0xC: "wall_L_down_left.png",
            0x6: "wall_L_down_right.png",
            0x7: "wall_U_left.png",
            0xB: "wall_U_upper.png",
            0xD: "wall_U_right.png",
            0xE: "wall_U_down.png",
        }
        surface = pygame.Surface((cols * cell_size, rows * cell_size))
        tile_cache: dict[str, pygame.Surface | None] = {}

        def get_tile(filename: str) -> pygame.Surface | None:
            """Load and cache a maze tile image."""
            if filename not in tile_cache:
                path = os.path.join(tile_dir, filename)
                if not os.path.exists(path):
                    tile_cache[filename] = None
                else:
                    img = pygame.image.load(path).convert_alpha()
                    if img.get_size() != (cell_size, cell_size):
                        img = pygame.transform.smoothscale(
                            img, (cell_size, cell_size)
                        )
                    tile_cache[filename] = img
            return tile_cache[filename]

        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                if cell == 0:
                    continue
                pos = (x * cell_size, y * cell_size)
                if cell == 0xF:
                    for fn in (
                        "wall_horizontal.png", "wall_vertical.png"
                    ):
                        tile = get_tile(fn)
                        if tile is not None:
                            surface.blit(tile, pos)
                    continue
                filename = tile_map.get(cell)
                if filename is None:
                    continue
                tile = get_tile(filename)
                if tile is not None:
                    surface.blit(tile, pos)
        return surface

    @surface.setter
    def surface(self, surface: pygame.Surface) -> None:
        """Set the widget surface and update its dimensions."""
        self.width, self.height = surface.get_size()
        self._surface = surface

    def generate(self, size: tuple[int, int], seed: int = 42) -> None:
        """Generate a maze with the specified size and seed."""
        generator = MazeGenerator(size=size, seed=seed)
        self.maze = generator.maze
        self.size = (
            (len(self.maze[0]) * self.cell_size) + self.thickness,
            (len(self.maze) * self.cell_size) + self.thickness
        )

    def neighbors(self, cell: tuple[int, int]) -> list[str]:
        """Return the valid directions available from a maze cell."""
        neighbors: list[str] = []

        def validate(x: int, y: int) -> bool:
            """Check whether the specified maze coordinates are valid."""
            if x < 0 or x > len(self.maze[0]) - 1:
                return False
            if y < 0 or y > len(self.maze) - 1:
                return False
            return True

        cell_x, cell_y = cell
        cell_v: int = self.maze[cell_y][cell_x]
        if cell_v & 1 == 0 and validate(cell_x, cell_y - 1):
            neighbors.append('N')
        if cell_v & 2 == 0 and validate(cell_x + 1, cell_y):
            neighbors.append('E')
        if cell_v & 4 == 0 and validate(cell_x, cell_y + 1):
            neighbors.append('S')
        if cell_v & 8 == 0 and validate(cell_x - 1, cell_y):
            neighbors.append('W')
        return neighbors

    def navigate(
        self,
        cell: tuple[int, int],
        direction: str
    ) -> tuple[int, int] | None:
        """Return the destination cell if movement is possible."""
        cell_x, cell_y = cell
        cell_value: int = self.maze[cell_y][cell_x]
        if direction == 'N':
            if cell_value & 1:
                return None
            cell_y -= 1
        if direction == 'E':
            if cell_value & 2:
                return None
            cell_x += 1
        if direction == 'S':
            if cell_value & 4:
                return None
            cell_y += 1
        if direction == 'W':
            if cell_value & 8:
                return None
            cell_x -= 1
        return (cell_x, cell_y)

    def CellToPosition(self, cell: tuple[int, int]) -> tuple[int, int]:
        """Convert a maze cell coordinate into a pixel position."""
        cell_left, cell_top = cell
        return (self.cell_size * cell_left, self.cell_size * cell_top)
