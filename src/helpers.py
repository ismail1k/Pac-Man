"""
Core classes and utilities for widgets, gameplay, input, audio, and cheats.
"""

import pygame
import inspect
from abc import ABC
from typing import Any, Callable
from threading import Timer
from pathlib import Path


class Widget(ABC):
    """Base class for visual elements rendered on a Pygame surface."""

    def __init__(
        self,
        surface: pygame.Surface,
        position: tuple[int, int] = (0, 0),
        offset: tuple[int, int] = (0, 0)
    ) -> None:
        """Initialize the widget with its surface, position, and offset."""
        self._surface: pygame.Surface = surface
        self._visible: bool | Callable = True
        self.left, self.top = position
        self.width, self.height = surface.get_size()
        self.offset_x, self.offset_y = offset
        self.padding: dict = {
            'left': 0, 'bottom': 0, 'right': 0, 'top': 0
        }

    @property
    def surface(self) -> pygame.Surface:
        """Return the surface used to render the widget."""
        return self._surface

    @surface.setter
    def surface(self, surface: pygame.Surface) -> None:
        """Set the widget surface and update its dimensions."""
        self.width, self.height = surface.get_size()
        self._surface = surface

    @property
    def position(self) -> tuple[int, int]:
        """Return the widget's position including offsets and padding."""
        return (
            self.left + self.offset_x + self.padding['left'],
            self.top + self.offset_y + self.padding['top']
        )

    @position.setter
    def position(self, position: tuple[int, int]) -> None:
        """Set the widget's base position."""
        self.left, self.top = position

    @property
    def size(self) -> tuple[int, int]:
        """Return the widget's size including padding."""
        return (
            self.width + self.padding['left'] + self.padding['right'],
            self.height + self.padding['top'] + self.padding['bottom']
        )

    @size.setter
    def size(self, size: tuple[int, int]) -> None:
        """Resize the widget's surface and update its dimensions."""
        self.width, self.height = size
        self._surface = pygame.transform.scale(self._surface, size)

    @property
    def offset(self) -> tuple[int, int]:
        """Return the widget's positional offset."""
        return (self.offset_x, self.offset_y)

    @offset.setter
    def offset(self, offset: tuple[int, int]) -> None:
        """Set the widget's positional offset."""
        self.offset_x, self.offset_y = offset

    @property
    def visible(self) -> bool:
        """Return whether the widget is currently visible."""
        if isinstance(self._visible, Callable):
            return self._visible()
        return self._visible

    @visible.setter
    def visible(self, visibility: bool | Callable) -> None:
        """Set the widget's visibility state or visibility callback."""
        self._visible = visibility

    def render(self, visual: Any) -> None:
        """Render the widget on the provided visual surface."""
        if self.visible:
            visual.screen.blit(self.surface, self.position)


class Playable(ABC):
    """Base class for objects that move and interact with the game canvas."""

    def __init__(self, canvas: Any, states: dict = {}) -> None:
        """Initialize the playable object with its canvas and game states."""
        self.canvas: Any = canvas
        self.states: dict = states
        self.visible: bool = False
        self.cell: tuple[int, int] = (0, 0)
        self.speed: float = 1.3
        self.direction: str = ''
        self._cache: dict = {}

    def reset(self) -> None:
        """Clear the cached movement state."""
        self._cache = {}

    def thread(self) -> None:
        """Update the object's movement and handle its behavior."""
        if not self.visible or self.states.get('pause') or self.states.get('freeze'):
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
            target: tuple[int, int] | None = self.canvas.navigate(
                self.cell, direction
            )

            if direction and target:
                self.direction = direction
                if self.canvas.navigate(target, direction):
                    self._cache.update({'direction': direction})

            if direction and not target:
                self._cache.update({'direction': ''})

    def spawn(
        self,
        cell_left: int | None = None,
        cell_top: int | None = None,
        delay: int = 0
    ) -> None:
        """Spawn the object at the specified cell after an optional delay."""
        from src.parsing import Configuration

        def _spawn(x: int, y: int) -> None:
            self.direction = ""
            self.cell = (x, y)
            self.position = self.canvas.CellToPosition(self.cell)
            self.visible = True

        if cell_left is None:
            cell_left = int((Configuration.get('width', 18) / 2) - 0.5)

        if cell_top is None:
            cell_top = int((Configuration.get('height', 12) / 2) - 0.5)

        if cell_left < 0:
            cell_left = len(self.canvas.maze[0]) - 1

        if cell_top < 0:
            cell_top = len(self.canvas.maze) - 1

        if delay == 0:
            return _spawn(cell_left, cell_top)

        Timer(delay, _spawn, args=(cell_left, cell_top)).start()

    def dispawn(self) -> None:
        """Remove the object from the game and reset its cell position."""
        self.visible = False
        self.cell = (-1, -1)
        self.position = (-1, -1)


class Controller(ABC):
    """Handles keyboard and controller input events."""

    ACTION_UP = [pygame.K_UP, pygame.K_w]
    ACTION_DOWN = [pygame.K_DOWN, pygame.K_s]
    ACTION_LEFT = [pygame.K_LEFT, pygame.K_a]
    ACTION_RIGHT = [pygame.K_RIGHT, pygame.K_d]
    ACTION_PAUSE = [pygame.K_p]
    ACTION_CONFIRM = [pygame.K_RETURN, 0]
    ACTION_BACK = [pygame.K_BACKSPACE, 1]
    ACTION_QUIT = [pygame.K_ESCAPE, pygame.K_q]

    INPUT_KEYBOARD = (
        [pygame.K_a + i for i in range(26)] +
        [pygame.K_0 + i for i in range(10)] +
        [pygame.K_SPACE]
    )

    def __init__(self) -> None:
        """Initialize the controller with an empty event list."""
        self.__events: list[tuple[int, Callable]] = []

    def onClick(self, actions: list[int], callback: Callable) -> None:
        """Register a callback for the specified input actions."""
        for action in actions:
            self.__events.append((action, callback))

    def listenControllerEvents(
        self,
        events: list[pygame.event.Event]
    ) -> None:
        """Process keyboard and controller events and trigger callbacks."""
        def trigger(key: int) -> None:
            for event, callback in self.__events:
                if event == key:
                    if len(inspect.signature(callback).parameters):
                        callback(key)
                    else:
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
        """Remove callbacks for the specified actions or clear all callbacks."""
        if len(actions):
            condition: Callable = lambda event, _: event not in actions
            self.__events = list(filter(condition, self.__events))
        else:
            self.__events.clear()


class Audio:
    """Provides static methods for controlling game audio."""

    _song: str | None = None

    @staticmethod
    def play(song: str) -> None:
        """Load and continuously play the specified song."""
        Audio._song = song
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(-1)

    @staticmethod
    def volume(level: float = 1.0) -> None:
        """Set the music volume to the specified level."""
        pygame.mixer.music.set_volume(level)

    @staticmethod
    def menu(song: str = "assets/audios/menu.mp3") -> None:
        """Play the menu music if it is not already playing."""
        if Audio._song != song:
            Audio.play(song)
            Audio.volume(1.0)

    @staticmethod
    def music(song: str = "assets/audios/music.mp3") -> None:
        """Play the game music if it is not already playing."""
        if Audio._song != song:
            Audio.play(song)
            Audio.volume(0.3)

    @staticmethod
    def coin(song: str = "assets/audios/coin.mp3") -> None:
        """Play the specified sound effect."""
        if Audio._song != song:
            pygame.mixer.Sound(song).play()


class Utils:
    """Provides general utility functions for the application."""

    @staticmethod
    def save(
        filename: str,
        content: str = "",
        override: bool = True
    ) -> None:
        """Save text content to a file, optionally preventing overwrites."""
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists() and not override:
            return

        path.write_text(content, encoding="utf-8")


class Cheat:
    """Stores and toggles gameplay cheat states."""

    invincibility = False
    level = False
    ghost_freeze = False
    extra_lives = False
    increased_speed = False

    @staticmethod
    def set_invincibility() -> None:
        """Toggle the invincibility cheat."""
        Cheat.invincibility = not Cheat.invincibility

    @staticmethod
    def set_increased_speed() -> None:
        """Toggle the increased speed cheat."""
        Cheat.increased_speed = not Cheat.increased_speed

    @staticmethod
    def set_ghost_freeze() -> None:
        """Toggle the ghost freeze cheat."""
        Cheat.ghost_freeze = not Cheat.ghost_freeze

    @staticmethod
    def set_level() -> None:
        """Toggle the level cheat."""
        Cheat.level = not Cheat.level

    @staticmethod
    def set_extra_lives() -> None:
        """Toggle the extra lives cheat."""
        Cheat.extra_lives = not Cheat.extra_lives
