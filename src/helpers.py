import pygame
from abc import ABC
from functools import wraps
from typing import Any, Callable


class Widget(ABC):
    def __init__(self, surface: pygame.Surface, position: tuple[int, int] = (0, 0), offset: tuple[int, int] = (0, 0)) -> None:
        self._surface: pygame.Surface = surface
        self._visible: bool | Callable = True
        self.left, self.top = position
        self.width, self.height = surface.get_size()
        self.offset_x, self.offset_y = offset
        self.padding: dict = {'left': 0, 'bottom': 0, 'right': 0, 'top': 0}

    @property
    def surface(self) -> pygame.Surface:
        return self._surface

    @surface.setter
    def surface(self, surface: pygame.Surface) -> None:
        self.width, self.height = surface.get_size()
        self._surface = surface

    @property
    def position(self) -> tuple[int, int]:
        return (self.left + self.offset_x + self.padding['left'], self.top + self.offset_y + self.padding['top'])

    @position.setter
    def position(self, position: tuple[int, int]) -> None:
        self.left, self.top = position

    @property
    def size(self) -> tuple[int, int]:
        return (
            self.width + self.padding['left'] + self.padding['right'],
            self.height + self.padding['top'] + self.padding['bottom']
        )

    @size.setter
    def size(self, size: tuple[int, int]) -> None:
        self.width, self.height = size
        self._surface = pygame.transform.scale(self._surface, size)

    @property
    def offset(self) -> tuple[int, int]:
        return (self.offset_x, self.offset_y)

    @offset.setter
    def offset(self, offset: tuple[int, int]) -> None:
        self.offset_x, self.offset_y = offset

    @property
    def visible(self) -> bool:
        if isinstance(self._visible, Callable):
            return self._visible()
        return self._visible

    @visible.setter
    def visible(self, visible: bool | Callable) -> None:
        self._visible = visible

    def render(self, visual: Any) -> None:
        if self.visible:
            visual.screen.blit(self.surface, self.position)


class Playable(ABC):
    def __init__(self, canvas: Any, states: dict = {}) -> None:
        self.canvas: Any = canvas
        self.states: dict = states
        self.cell: tuple[int, int] = (0, 0)
        self.speed: float = 2
        self.direction: str = ''
        self._cache: dict = {}

    def reset(self) -> None:
        self._cache = {}

    def thread(self) -> None:
        if self.states.get('pause') or self.states.get('freeze'):
            return None
        if self.direction:
            target = self.canvas.navigate(self.cell, self.direction)
            target_x, target_y = self.canvas.CellToPosition(target)
            if abs(self.left - target_x) <= self.speed:
                self.left = target_x
            elif self.left < target_x:
                self.left += self.speed
            elif self.left > target_x:
                self.left -= self.speed
            if abs(self.top - target_y) <= self.speed:
                self.top = target_y
            elif self.top < target_y:
                self.top += self.speed
            elif self.top > target_y:
                self.top -= self.speed
            if self.left == target_x and self.top == target_y:
                self.cell = target
                if hasattr(self, 'behaviour'):
                    self.behaviour()
                direction = self._cache.get("direction")
                if direction and self.canvas.navigate(self.cell, direction):
                    self.direction = direction
                elif self.direction and self.canvas.navigate(self.cell, self.direction):
                    pass
                else:
                    self.direction = ""
        if not self.direction:
            if hasattr(self, 'behaviour'):
                self.behaviour()
            direction: str | None = self._cache.get('direction')
            target: tuple[int, int] | None = self.canvas.navigate(self.cell, direction)
            if direction and target:
                self.direction = direction
                if self.canvas.navigate(target, direction):
                    self._cache.update({'direction': direction})
            if direction and not target:
                self._cache.update({'direction': ''})

    def spawn(self, cell_left: int, cell_top: int) -> None:
        from src.playground import Canvas

        if cell_left < 0:
            cell_left = len(self.canvas.maze[0]) - 1
        if cell_top < 0:
            cell_top = len(self.canvas.maze) - 1
        self.direction = ""
        self.cell = (cell_left, cell_top)
        self.position = self.canvas.CellToPosition(self.cell)


class Controller(ABC):
    ACTION_UP = [pygame.K_UP, pygame.K_w]
    ACTION_DOWN = [pygame.K_DOWN, pygame.K_s]
    ACTION_LEFT = [pygame.K_LEFT, pygame.K_a]
    ACTION_RIGHT = [pygame.K_RIGHT, pygame.K_d]
    ACTION_PAUSE = [pygame.K_p]
    ACTION_CONFIRM = [pygame.K_RETURN, 0]
    ACTION_BACK = [pygame.K_BACKSPACE, 1]
    ACTION_QUIT = [pygame.K_ESCAPE, pygame.K_q]
    def __init__(self) -> None:
        self.__events: list[tuple[int, Callable]] = []

    def onClick(self, actions: list[int], callback: Callable) -> None:
        for action in actions:
            self.__events.append((action, callback))

    def listenControllerEvents(self, events: list[pygame.event.Event]) -> None:
        def trigger(key: int) -> None:
            for event, callback in self.__events:
                if event == key:
                    callback()

        for event in events:
            if event.type == pygame.KEYDOWN:
                trigger(event.key)
            if event.type == pygame.JOYBUTTONDOWN:
                trigger(event.button)
            if event.type == pygame.JOYHATMOTION:
                hat_x, hat_y = event.value
                if hat_y == 1:
                    trigger(pygame.K_UP)
                elif hat_y == -1:
                    trigger(pygame.K_DOWN)
                if hat_x == 1:
                    trigger(pygame.K_RIGHT)
                elif hat_x == -1:
                    trigger(pygame.K_LEFT)

    def destroyControllerEvents(self, actions: list[int] = []) -> None:
        if len(actions):
            condition: Callable = lambda event, _: event not in actions
            self.__events = list(filter(condition, self.__events))
        else:
            self.__events.clear()
