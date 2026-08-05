import pygame, random, os
from time import time
from typing import Any, Callable
from mazegenerator import MazeGenerator
from src.parsing import Configuration
from src.visualizer import Visualizer
from src.helpers import Widget, Playable, Controller


class Reward(Widget, Playable):
    textures: list[str] = [
        "assets/images/point.png",
        "assets/images/coin_special.png",
    ]
    def __init__(self, canvas: Any, states: dict = {}, special: bool = False) -> None:
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
    textures: list[str] = [
        "assets/images/player_close.png",
        "assets/images/player_open.png",
    ]
    def __init__(self, canvas: Any, states: dict = {}) -> None:
        Widget.__init__(self, pygame.Surface((0, 0)))
        Playable.__init__(self, canvas, states)
        Controller.__init__(self)
        self.onClick(self.ACTION_UP, lambda: self._cache.update({'direction': "N"}))
        self.onClick(self.ACTION_DOWN, lambda: self._cache.update({'direction': "S"}))
        self.onClick(self.ACTION_LEFT, lambda: self._cache.update({'direction': "W"}))
        self.onClick(self.ACTION_RIGHT, lambda: self._cache.update({'direction': "E"}))
        self.padding.update({'left': 15, 'bottom': 15, 'right': 15, 'top': 15})
        self.speed: float = 2.0

    @property
    def surface(self) -> pygame.Surface:
        mouth: int = 0
        angle: int = 0
        flip: bool = False
        if self.direction == 'E':
            mouth = 1
            angle = 0
        if self.direction == 'N':
            mouth = 1
            angle = 90
        if self.direction == 'W':
            mouth = 1
            angle = 180
            flip = True
        if self.direction == 'S':
            mouth = 1
            angle = 270
        surface = pygame.image.load(self.textures[mouth]).convert_alpha()
        surface = pygame.transform.smoothscale(surface, (35, 35))
        surface = pygame.transform.flip(surface, False, flip)
        return pygame.transform.rotate(surface, angle)

    def onDestroy(self) -> None:
        self.destroyControllerEvents()

    def render(self, visual: Visualizer) -> None:
        self.listenControllerEvents(visual.events)
        self.thread()
        if self.visible:
            visual.screen.blit(self.surface, self.position)


class Ghost(Widget, Playable):
    textures: list[str] = [
        "assets/images/ghost_blue.png",
        "assets/images/ghost_green.png",
        "assets/images/ghost_pink.png",
        "assets/images/ghost_red.png",
        "assets/images/enemy_fear_white.png",
    ]
    def __init__(self, canvas: Any, states: dict = {}) -> None:
        Widget.__init__(self, pygame.Surface((0, 0)))
        Playable.__init__(self, canvas, states)
        self.scared_at: float = 0.0
        self.init_cell: tuple[int, int] = (0, 0)
        self.padding.update({'left': 15, 'bottom': 15, 'right': 15, 'top': 15})
        self.type: int = 0

    @property
    def surface(self) -> pygame.Surface:
        surface = pygame.image.load(self.textures[self.type]).convert_alpha()
        if self.scared_at + 15 > time():
            cooldown = int(abs(time() - self.scared_at - 15))
            surface = pygame.image.load(self.textures[-1]).convert_alpha()
            if cooldown <= 5:
                if cooldown % 2 == 0:
                    surface = pygame.image.load(self.textures[self.type]).convert_alpha()
        return pygame.transform.smoothscale(surface, (35, 35))

    def behaviour(self):
        def reverse(direction: str) -> str:
            if direction == 'N':
                return 'S'
            if direction == 'S':
                return 'N'
            if direction == 'E':
                return 'W'
            if direction == 'W':
                return 'E'
            return ''
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

    def render(self, visual: Visualizer) -> None:
        self.thread()
        if self.visible:
            visual.screen.blit(self.surface, self.position)


class Canvas(Widget):
    thickness = 5
    cell_size: int = 60
    def __init__(self) -> None:
        super().__init__(pygame.Surface((0, 0)))
        self.maze: list[list[int]] = []

    @property
    def surface(self) -> pygame.Surface:
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
        tile_cache = {}
        def get_tile(filename):
            if filename not in tile_cache:
                path = os.path.join(tile_dir, filename)
                if not os.path.exists(path):
                    tile_cache[filename] = None
                else:
                    img = pygame.image.load(path).convert_alpha()
                    if img.get_size() != (cell_size, cell_size):
                        img = pygame.transform.smoothscale(img, (cell_size, cell_size))
                    tile_cache[filename] = img
            return tile_cache[filename]
        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                if cell == 0:
                    continue
                pos = (x * cell_size, y * cell_size)
                if cell == 0xF:
                    for filename in ("wall_horizontal.png", "wall_vertical.png"):
                        tile = get_tile(filename)
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

    def generate(self, size: tuple[int, int], seed: int = 42) -> None:
        generator = MazeGenerator(size=size, seed=seed)
        self.maze = generator.maze
        self.size = (
            (len(self.maze[0]) * self.cell_size) + self.thickness,
            (len(self.maze) * self.cell_size) + self.thickness
        )

    def neighbors(self, cell: tuple[int, int]) -> list[tuple[int, int]]:
        neighbors: list[tuple[int, int]] = []
        def validate(x: int, y: int) -> bool:
            if x < 0 or x > len(self.maze[0]) - 1:
                return False
            if y < 0 or y > len(self.maze) - 1:
                return False
            return True
        cell_x, cell_y = cell
        cell: int = self.maze[cell_y][cell_x]
        if cell & 1 == 0 and validate(cell_x, cell_y - 1):
            neighbors.append('N')
        if cell & 2 == 0 and validate(cell_x + 1, cell_y):
            neighbors.append('E')
        if cell & 4 == 0 and validate(cell_x, cell_y + 1):
            neighbors.append('S')
        if cell & 8 == 0 and validate(cell_x - 1, cell_y):
            neighbors.append('W')
        return neighbors

    def navigate(self, cell: tuple[int, int], direction: str) -> tuple[int, int] | None:
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
        cell_left, cell_top = cell
        return (self.cell_size * cell_left, self.cell_size * cell_top)
