import pygame
from abc import ABC
from src.interface import VContainer, VImage, VText
from src.visualizer import Visualizer, Widget
from src.helpers import Controller
from src.playground import Gameplay


class Screen(Widget, ABC):
    def __init__(self, scene: Widget) -> None:
        Widget.__init__(self, pygame.Surface(Visualizer.resolution))
        self.scene: Widget = scene

    def render(self, visual: Visualizer) -> None:
        self.scene.render(visual)


class GameplayScreen(Screen):
    def __init__(self, gameplay: Gameplay) -> None:
        screen_w, screen_h = Visualizer.resolution
        image: Widget = VImage("assets/images/pac-man-logo.png")
        image.left += (gameplay.width/2) - (image.width/2) - 25
        image.top -= image.height + 10
        score: Widget = VText(lambda: f"Score: {gameplay.states.get('score')}")
        score.top -= score.height + 10
        hearts = VContainer([
            VImage(
                "assets/images/player_open.png", size=(40, 40),
                visible=lambda: gameplay.states.get('hearts') >= 1
            ),
            VImage(
                "assets/images/player_open.png", size=(40, 40),
                visible=lambda: gameplay.states.get('hearts') >= 2
            ),
            VImage(
                "assets/images/player_open.png", size=(40, 40),
                visible=lambda: gameplay.states.get('hearts') >= 3
            ),
        ], inline=True)
        hearts.offset_x += gameplay.width - hearts.width
        hearts.offset_y -= hearts.height + 10
        super().__init__(
            VContainer(
                [gameplay, score, image, hearts],
                visible=lambda: not gameplay.states.get('pause'),
                fullscreen=True,
                absolute=True,
            )
        )


class PauseScreen(Screen):
    def __init__(self, states: dict = {}) -> None:
        super().__init__(
            VContainer([
                VImage("assets/images/pac-man-logo.png", size=(289 * 2, 70 * 2)),
                VText("Pause", position=(210, 20)),
            ], visible=lambda: self.states.get('pause'))
        )
        self._cache: dict = {}
        self.states: dict = states

    def control(self, controller: Controller) -> None:
        actions: list[int] = []
        self.controller: Controller = controller
        def toggle() -> None:
            self.states.update({'pause': not self.states.get('pause')})
        actions.extend(self.controller.onclick(Controller.ACTION_PAUSE, (toggle, ())))
        self._cache.update({'controller_actions': actions})

    def OnDestroy(self) -> None:
        self.controller.destroy(self.actions)

