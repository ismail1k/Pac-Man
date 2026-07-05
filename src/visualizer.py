import pygame
from typing import Any, Callable
from abc import ABC, abstractmethod
from src.parsing import Configuration
from src.helpers import Controller


class Widget(ABC):
    def __init__(self, surface: pygame.Surface, position: tuple[int, int] = (0, 0), offset: tuple[int, int] = (0, 0)) -> None:
        self._surface: pygame.Surface = surface
        self.left, self.top = position
        self.width, self.height = surface.get_size()
        self.offset_x, self.offset_y = offset
        self.padding: dict = {'left': 0, 'bottom': 0, 'right': 0, 'top': 0}
        self._visible: bool | Callable = True

    @property
    def surface(self) -> pygame.Surface:
        return self._surface

    @surface.setter
    def surface(self, surface: pygame.Surface) -> None:
        self._surface = surface

    @property
    def position(self) -> tuple[int, int]:
        return (self.left + self.offset_x, self.top + self.offset_y)

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

    def OnDestroy(self) -> None:
        pass


class Visualizer:
    framerate: int = 60
    resolution: tuple = (1920, 1080)

    def __init__(self, config: Configuration) -> None:
        pygame.init()
        info = pygame.display.Info()
        # Visualizer.resolution = (info.current_w, info.current_h)
        self.screen = pygame.display.set_mode(self.resolution)
        self.controller: Controller | None = None
        self.scenes: list[Widget] = []

    def clear(self) -> None:
        for element in self.scenes:
            element.OnDestroy()
        self.scenes.clear()
    
    def render(self) -> None:
        runtime = True
        clock = pygame.time.Clock()
        pygame.mouse.set_visible(False)
        while runtime:
            self.screen.fill((0, 0, 0))
            self.events: list = pygame.event.get()
            for event in self.events:
                if event.type == pygame.QUIT:
                    runtime = False
                if event.type == pygame.JOYDEVICEADDED:
                    self.controller.joystick(pygame.joystick.Joystick(event.device_index))
                if event.type == pygame.KEYDOWN:
                    self.controller.listen(event.key)
                    if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                        runtime = False
                if event.type == pygame.JOYBUTTONDOWN:
                    self.controller.listen(event.button)
                if event.type == pygame.JOYHATMOTION:
                    hat_x, hat_y = event.value
                    if hat_y == 1:
                        self.controller.listen(pygame.K_UP)
                    elif hat_y == -1:
                        self.controller.listen(pygame.K_DOWN)
                    if hat_x == 1:
                        self.controller.listen(pygame.K_RIGHT)
                    elif hat_x == -1:
                        self.controller.listen(pygame.K_LEFT)
            for element in self.scenes:
                if element.visible:
                    element.render(self)
            pygame.display.update()
            pygame.display.flip()
            clock.tick(self.framerate)
        pygame.quit()
