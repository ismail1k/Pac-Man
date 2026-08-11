"""
Visual components and containers used to build the application's interface.
"""
import pygame
from typing import Any, Callable
from src.helpers import Controller
from src.visualizer import Visualizer, Widget


class VImage(Widget):
    """Widget that displays an image loaded from a file."""

    def __init__(
        self,
        path: str,
        position: tuple[int, int] = (0, 0),
        size: tuple[int, int] = (0, 0),
        visible: Callable | bool = True
    ) -> None:
        """
        Initialize an image widget with its path, position,
        size, and visibility.
        """
        surface = pygame.image.load(path).convert_alpha()
        if size[0] and size[1]:
            surface = pygame.transform.smoothscale(surface, size)
        super().__init__(surface, position)
        self.visible = visible


class VText(Widget):
    """Widget that displays static or dynamically generated text."""

    def __init__(
        self,
        content: str | Callable,
        position: tuple[int, int] = (0, 0),
        color: tuple[int, int, int] = (255, 255, 255),
        size: int = 24
    ) -> None:
        """Initialize a text widget with its content, position, and color."""
        self._content: str | Callable = content
        self.font = pygame.font.Font(
            "assets/fonts/PressStart2P-Regular.ttf", size
        )
        super().__init__(self.font.render(
            str(self.content), True, color
        ), position)
        self.color: tuple[int, int, int] = color

    @property
    def content(self) -> str | None:
        """Return the current text content."""
        if callable(self._content):
            return str(self._content())
        return self._content

    @content.setter
    def content(self, content: str | Callable) -> None:
        """Set the text content or content callback."""
        self._content = content

    def render(self, visual: Any) -> None:
        """Render the current text content on the visualizer."""
        self.surface = self.font.render(
            str(self.content), True, self.color
        )
        visual.screen.blit(self.surface, self.position)


class VField(Widget):
    """Widget that displays text inside a bordered field."""

    def __init__(
        self,
        content: str | Callable,
        position: tuple[int, int] = (0, 0)
    ) -> None:
        """Initialize a field widget with its content and position."""
        self._content: str | Callable = content
        self.font = pygame.font.Font(
            "assets/fonts/PressStart2P-Regular.ttf", 24
        )
        super().__init__(
            self.font.render(self.content, True, (255, 255, 255)),
            position
        )
        self.padding.update({'left': 10, 'bottom': 10, 'right': 10, 'top': 10})

    @property
    def surface(self) -> pygame.surface.Surface:
        """Create and return the rendered field surface."""
        surface = pygame.surface.Surface(
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

    @surface.setter
    def surface(self, surface: pygame.surface.Surface) -> None:
        """Set the widget surface and update its dimensions."""
        self.width, self.height = surface.get_size()
        self._surface = surface

    @property
    def content(self) -> str:
        """Return the current field content."""
        if callable(self._content):
            return str(self._content())
        return self._content

    @content.setter
    def content(self, content: str | Callable) -> None:
        """Set the field content or content callback."""
        self._content = content

    def render(self, visual: Any) -> None:
        """Render the field on the visualizer."""
        visual.screen.blit(self.surface, self.position)


class VOption(Widget):
    """Widget representing a selectable option."""

    def __init__(
        self,
        label: str,
        onselect: Callable,
        position: tuple[int, int] = (0, 0)
    ) -> None:
        """Initialize an option with its label and selection callback."""
        self.font = pygame.font.Font(
            "assets/fonts/PressStart2P-Regular.ttf", 28
        )
        super().__init__(
            self.font.render(label, True, (255, 255, 255)),
            position
        )
        self.label: str = label
        self.onselect: Callable = onselect
        self.focus: bool = False
        self.padding.update({'top': 7, 'bottom': 7})

    def render(self, visual: Any) -> None:
        """Render the option using its current focus state."""
        color: tuple[int, int, int] = (255, 255, 255)
        if self.focus:
            color = (255, 0, 0)
        visual.screen.blit(
            self.font.render(self.label, True, color),
            self.position
        )


class VSelect(Widget, Controller):
    """Widget that allows navigation and selection between multiple options."""

    def __init__(
        self,
        options: list[VOption],
        position: tuple[int, int] = (0, 0),
        visible: bool | Callable = True,
        inline: bool = False
    ) -> None:
        """Initialize a selection widget with its options and layout."""
        Widget.__init__(self, pygame.surface.Surface((0, 0)), position)
        Controller.__init__(self)
        self.options: list[VOption] = options
        self.inline: bool = inline
        self.focus: int = 0
        self.visible = visible
        self.adjust()
        self.controller()

    def adjust(self) -> None:
        """Calculate the size and position of the selection options."""
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
        """Configure controller actions for navigating and selecting."""
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
        """Render the options and process controller events."""
        self.listenControllerEvents(visual.events)
        for index, option in enumerate(self.options):
            option.focus = False
            if self.focus == index:
                option.focus = True
            option.render(visual)

    def onDestroy(self) -> None:
        """Remove all controller events associated with the selection."""
        self.destroyControllerEvents()


class VContainer(Widget):
    """Widget that groups and arranges multiple visual elements."""

    def __init__(
        self,
        elements: list[Any],
        position: tuple[int, int] = (0, 0),
        visible: bool | Callable = True,
        absolute: bool = False,
        fullscreen: bool = False,
        inline: bool = False
    ) -> None:
        """Initialize a container with its elements and layout settings."""
        super().__init__(pygame.surface.Surface((0, 0)), position)
        self.elements: list[Any] = elements
        self.fullscreen: bool = fullscreen
        self.absolute: bool = absolute
        self.inline: bool = inline
        self.visible = visible
        self.adjust()

    def adjust(self) -> None:
        """Calculate the container size and position its elements."""
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
        """Render all elements contained in the container."""
        if self.visible:
            for element in self.elements:
                element.render(visual)

    def OnDestroy(self) -> None:
        """Destroy all contained elements and clear the container."""
        for element in self.elements:
            element.OnDestroy()
        self.elements.clear()
