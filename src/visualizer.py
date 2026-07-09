import pygame
from typing import Any, Callable
from src.parsing import Configuration
from src.helpers import Widget, Controller


class Visualizer:
    framerate: int = 60
    resolution: tuple = (1920, 1080)

    def __init__(self, config: Configuration) -> None:
        pygame.init()
        info = pygame.display.Info()
        Visualizer.resolution = (info.current_w, info.current_h)
        self.screen = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN)
        self.scenes: list[Widget] = []

    def clear(self) -> None:
        for element in self.scenes:
            if hasattr(element, 'onDestroy'):
                element.onDestroy()
        self.scenes.clear()
    
    def render(self) -> None:
        runtime = True
        clock = pygame.time.Clock()
        pygame.mouse.set_visible(False)
        while runtime:
            self.events: list = pygame.event.get()
            self.screen.fill((0, 0, 0))
            for event in self.events:
                if event.type == pygame.QUIT:
                    runtime = False
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                        runtime = False
            for element in self.scenes:
                if element.visible:
                    element.render(self)
            pygame.display.update()
            pygame.display.flip()
            clock.tick(self.framerate)
        pygame.quit()
