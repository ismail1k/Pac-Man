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
        self.font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 28)
        super().__init__(self.font.render("", True, color), position)
        self.padding.update({'top': 7, 'bottom': 7})
        self.color: tuple[int, int, int] = color
        self.content: str | Callable = content

    def render(self, visual: Any) -> None:
        if isinstance(self.content, str):
            self.surface = self.font.render(self.content, True, self.color)
        if isinstance(self.content, Callable):
            self.surface = self.font.render(self.content(), True, self.color)
        visual.screen.blit(self.surface, self.position)


class VButton(Widget):
    def __init__(self, label: str, position: tuple[int, int] = (0, 0)) -> None:
        font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 24)
        super().__init__(font.render(label, True, (255, 255, 255)), position)


class VBlock(Widget):
    def __init__(self, size: tuple[int, int], position: tuple[int, int] = (0, 0)) -> None:
        super().__init__(pygame.Surface(size), position)


class VOption(Widget):
    def __init__(self, label: str, onselect: tuple[Callable, tuple], position: tuple[int, int] = (0, 0)) -> None:
        self.text = VText(label, color=(255, 255, 255))
        super().__init__(self.text.surface, position)
        self.padding = self.text.padding
        self.padding.update({'left': 5, 'right': 5})
        self.onselect: tuple[Callable, tuple] = onselect
        self.focus: bool = False

    def render(self, visual: Any) -> None:
        self.text.color = (255, 255, 255)
        if self.focus:
            self.text.color = (255, 0, 0)
        self.text.surface = self.text.font.render(self.text.content, True, self.text.color)
        visual.screen.blit(self.text.surface, self.position)


class VSelect(Widget):
    def __init__(self, options: list[VOption], controller: Controller, position: tuple[int, int] = (0, 0), visible: bool | Callable = True) -> None:
        super().__init__(pygame.Surface((0, 0)), position)
        self._cache: dict = {}
        self.options: list[VOption] = []
        self.focus: int = 0
        self.visible: bool | Callable = visible
        for option in options:
            option.offset_x = self.offset_x + self.left
            option.offset_y = self.offset_y + self.top
            option_w, option_h = option.size
            if self.width < option_w:
                self.width = option_w
            self.height += option_h
            self.options.append(option)
        self.controller: Controller = controller
        self.navigate(controller)
        self.size = (self.width, self.height)

    def navigate(self, controller: Controller) -> None:
        events: list[int] = []
        def up() -> None:
            if self.focus > 0:
                self.focus -= 1
        def down() -> None:
            if self.focus < len(self.options) - 1:
                self.focus += 1
        def select() -> None:
            function, args = self.options[self.focus].onselect
            function(*args)

        events.extend(controller.onclick(Controller.ACTION_UP, (up, ())))
        events.extend(controller.onclick(Controller.ACTION_DOWN, (down, ())))
        events.extend(controller.onclick(Controller.ACTION_CONFIRM, (select, ())))
        self._cache.update({'events': events})

    def render(self, visual: Any) -> None:
        offset_x, offset_y = (self.offset_x, self.offset_y)
        for index, option in enumerate(self.options):
            option.offset_x = offset_x + self.left
            option.offset_y = offset_y + self.top
            offset_y += option.size[1]
            option.focus = False
            if self.focus == index:
                option.focus = True
            option.render(visual)

    def OnDestroy(self) -> None:
        self.controller.destroy(self._cache.get('events'))


class VContainer(Widget):
    def __init__(self, elements: list[Any], position: tuple[int, int] = (0, 0),
        visible: bool | Callable = True, absolute: bool = False,
        fullscreen: bool = False, inline: bool = False
        ) -> None:
        super().__init__(pygame.Surface((0, 0)), position)
        self.visible: bool | Callable = visible
        self.fullscreen: bool = fullscreen
        self.absolute: bool = absolute
        self.inline: bool = inline
        self.elements: list[Any] = elements
        offset_x, offset_y = self.position
        for element in self.elements:
            element_width, element_height = element.size
            element_width += self.offset_x + element.offset_x + element.left
            element_height += self.offset_y + element.offset_y + element.top
            element.offset_x += offset_x
            element.offset_y += offset_y
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
            if isinstance(element, VContainer):
                element.adjust()
        if self.fullscreen:
            screen_width, screen_height = Visualizer.resolution
            self.offset_x = (screen_width/2) - (self.width/2)
            self.offset_y = (screen_height/2) - (self.height/2)
            for element in self.elements:
                element.offset_x += self.offset_x
                element.offset_y += self.offset_y
                if isinstance(element, VContainer):
                    element.adjust()

    def adjust(self) -> None:
        offset_x, offset_y = self.offset
        for element in self.elements:
            element.offset_x += offset_x
            element.offset_y += offset_y
            if isinstance(element, VContainer):
                element.adjust()

    def render(self, visual: Any) -> None:
        if self.visible:
            for element in self.elements:
                element.render(visual)

    def OnDestroy(self) -> None:
        for element in self.elements:
            element.OnDestroy()
        self.elements.clear()
