import pygame
from typing import Any, Callable
from abc import ABC, abstractmethod
from src.parsing import Configuration
from src.helpers import Controller
from src.visualizer import Visualizer, Widget


class VImage(Widget):
    def __init__(self, path: str, position: tuple[int, int] = (0, 0), size: tuple[int, int] = (0, 0), visible: Callable | bool = True) -> None:
        surface = pygame.image.load(path).convert_alpha()
        if size[0] and size[1]:
            surface = pygame.transform.smoothscale(surface, size)
        super().__init__(surface, position)
        self.visible = visible


class VText(Widget):
    def __init__(self, content: str | Callable, position: tuple[int, int] = (0, 0), color: tuple[int, int, int] = (255, 255, 255)) -> None:
        self._content: str | Callable = content
        self.font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 24)
        super().__init__(self.font.render(self.content, True, color), position)
        self.color: tuple[int, int, int] = color
        
    @property
    def content(self) -> bool:
        if isinstance(self._content, Callable):
            return self._content()
        return self._content

    @content.setter
    def content(self, content: bool | Callable) -> None:
        self._content = content

    def render(self, visual: Any) -> None:
        self.surface = self.font.render(self.content, True, self.color)
        visual.screen.blit(self.surface, self.position)


class VField(Widget):
    def __init__(self, content: str | Callable, position: tuple[int, int] = (0, 0)) -> None:
        self._content: str | Callable = content
        self.font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 24)
        super().__init__(self.font.render(self.content, True, (255, 255, 255)), position)
        self.padding.update({'left': 10, 'bottom': 10, 'right': 10, 'top': 10})

    @property
    def surface(self) -> pygame.Surface:
        surface = pygame.Surface(
            self.size,
            pygame.SRCALPHA
        )
        surface.fill((40, 40, 40))
        pygame.draw.rect(
            surface,
            (255, 255, 255),
            surface.get_rect(),
            width=2,
            border_radius=6
        )
        text = self.font.render(self.content, True, (255, 255, 255))
        text_rect = text.get_rect(
            midleft=(10, self.size[1] // 2)
        )
        surface.blit(text, text_rect)
        return surface

    @property
    def content(self) -> bool:
        if isinstance(self._content, Callable):
            return self._content()
        return self._content

    @content.setter
    def content(self, content: bool | Callable) -> None:
        self._content = content

    def render(self, visual: Any) -> None:
        visual.screen.blit(self.surface, self.position)


class VOption(Widget):
    def __init__(self, label: str, onselect: Callable, position: tuple[int, int] = (0, 0)) -> None:
        self.font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 28)
        super().__init__(self.font.render(label, True, (255, 255, 255)), position)
        self.label: str = label
        self.onselect: Callable = onselect
        self.focus: bool = False
        self.padding.update({'top': 7, 'bottom': 7})

    def render(self, visual: Any) -> None:
        color: tuple[int, int, int] = (255, 255, 255)
        if self.focus:
            color: tuple[int, int, int] = (255, 0, 0)
        visual.screen.blit(self.font.render(self.label, True, color), self.position)


class VSelect(Widget, Controller):
    def __init__(self, options: list[VOption], position: tuple[int, int] = (0, 0), visible: bool | Callable = True, inline: bool = False) -> None:
        Widget.__init__(self, pygame.Surface((0, 0)), position)
        Controller.__init__(self)
        self.options: list[VOption] = options
        self.visible: bool | Callable = visible
        self.inline: bool = inline
        self.focus: int = 0
        self.adjust()
        self.controller()

    def adjust(self) -> None:
        offset_x, offset_y = self.position
        for option in self.options:
            option.offset_x = offset_x
            option.offset_y = offset_y
            option_width, option_height = option.size
            if self.inline:
                offset_x += option_width
                self.width += option_width
                if self.height < option_height:
                    self.height = option_height
            else:
                offset_y += option_height
                self.height += option_height
                if self.width < option_width:
                    self.width = option_width

    def controller(self) -> None:
        def next() -> None:
            if self.focus > 0:
                self.focus -= 1
        def previous() -> None:
            if self.focus < len(self.options) - 1:
                self.focus += 1
        def select() -> None:
            self.options[self.focus].onselect()

        if self.inline:
            self.onClick(self.ACTION_LEFT, lambda: next())
            self.onClick(self.ACTION_RIGHT, lambda: previous())
        else:
            self.onClick(self.ACTION_UP, lambda: next())
            self.onClick(self.ACTION_DOWN, lambda: previous())
        self.onClick(self.ACTION_CONFIRM, lambda: select())

    def render(self, visual: Any) -> None:
        self.listenControllerEvents(visual.events)
        for index, option in enumerate(self.options):
            option.focus = False
            if self.focus == index:
                option.focus = True
            option.render(visual)

    def onDestroy(self) -> None:
        self.destroyControllerEvents()


class VContainer(Widget):
    def __init__(self, elements: list[Any], position: tuple[int, int] = (0, 0),
        visible: bool | Callable = True, absolute: bool = False,
        fullscreen: bool = False, inline: bool = False
        ) -> None:
        super().__init__(pygame.Surface((0, 0)), position)
        self.elements: list[Any] = elements
        self.visible: bool | Callable = visible
        self.fullscreen: bool = fullscreen
        self.absolute: bool = absolute
        self.inline: bool = inline
        self.adjust()

    def adjust(self) -> None:
        offset_x, offset_y = self.position
        for element in self.elements:
            element.offset_x = offset_x
            element.offset_y = offset_y
            element_width, element_height = element.size
            if self.absolute:
                if self.width < element_width:
                    self.width = element_width
                if self.height < element_height:
                    self.height = element_height
                continue
            if self.inline:
                offset_x += element_width
                self.width += element_width
                if self.height < element_height:
                    self.height = element_height
            else:
                offset_y += element_height
                self.height += element_height
                if self.width < element_width:
                    self.width = element_width
        if self.fullscreen:
            screen_width, screen_height = Visualizer.resolution
            self.left = (screen_width/2) - (self.width/2)
            self.top = (screen_height/2) - (self.height/2)
        for element in self.elements:
            element.offset_x += self.left
            element.offset_y += self.top
            if hasattr(element, 'adjust'):
                element.adjust()

    def render(self, visual: Any) -> None:
        if self.visible:
            for element in self.elements:
                element.render(visual)

    def OnDestroy(self) -> None:
        for element in self.elements:
            element.OnDestroy()
        self.elements.clear()
