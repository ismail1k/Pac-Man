import pygame, sys
from abc import ABC
from typing import Callable
from functools import partial
from src.visualizer import Visualizer
from src.interface import VContainer, VImage, VText, VSelect, VOption
from src.helpers import Widget, Controller
from src.playground import Gameplay


class Scene(Widget, ABC):
    def __init__(self, scene: Widget) -> None:
        Widget.__init__(self, pygame.Surface(Visualizer.resolution))
        self._scene: Widget = scene

    def render(self, visual: Visualizer) -> None:
        self._scene.render(visual)


class MainScreen(Scene):
    def __init__(self,
        play: Callable,
        leaderboard: Callable,
        instructions: Callable,
        ) -> None:
        pygame.mixer.music.load("assets/audios/menu.mp3")
        pygame.mixer.music.play(-1)
        super().__init__(
            VContainer([
                VImage("assets/images/pac-man-logo.png", size=(289 * 2, 70 * 2)),
                VSelect([
                    VOption("1 Start Game", onselect=lambda: play()),
                    VOption("2 View Highscores", onselect=lambda: leaderboard()),
                    VOption("3 Instructions", onselect=lambda: instructions()),
                    VOption("4 Exit", onselect=lambda: sys.exit(0)),
                ], position=(35, 20))
            ], fullscreen=True)
        )


class GameplayScreen(Scene, Controller):
    def __init__(self, gameplay: Gameplay, pause: Callable) -> None:
        Controller.__init__(self)
        self.gameplay: Gameplay = gameplay
        self.onClick(self.ACTION_PAUSE, lambda: pause())
        screen_w, screen_h = Visualizer.resolution
        image: Widget = VImage("assets/images/pac-man-logo.png")
        image.left += (gameplay.width/2) - (image.width/2)
        image.padding.update({'bottom': 10})
        image.top -= image.size[1]
        score: Widget = VText(lambda: f"Score: {self.gameplay.states.get('score')}")
        score.padding.update({'bottom': 10})
        score.top -= score.size[1]
        hearts = self._hearts()
        hearts.top = gameplay.height / 2
        hearts.padding.update({'top': 10})
        pygame.mixer.music.load("assets/audios/music.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
        Scene.__init__(self,
            VContainer(
                [gameplay, score, image, hearts],
                fullscreen=True,
                absolute=True,
            )
        )

    def _hearts(self) -> Widget:
        attempts: list[Widget] = []
        for index in range(3):
            image: VImage = VImage("assets/images/player_open.png", size=(40, 40))
            image.visible = partial(lambda index: self.gameplay.states.get('hearts') > index, index)
            attempts.append(image)
        return VContainer(attempts, inline=True)

    def render(self, visual: Visualizer) -> None:
        self.listenControllerEvents(visual.events)
        Scene.render(self, visual)


class PauseScreen(Scene):
    def __init__(self, resume: Callable, launch: Callable) -> None:
        Scene.__init__(self,
            VContainer(
                [
                    VImage("assets/images/pac-man-logo.png", size=(289 * 2, 70 * 2)),
                    VSelect([
                        VOption("1 Pause", onselect=lambda: resume()),
                        VOption("2 Main Menu", onselect=lambda: launch()),
                        VOption("2 Exit", onselect=lambda: sys.exit(0)),
                    ], position=(35, 20))
                ],
                fullscreen=True
            )
        )


class LeaderboardScreen(Scene):
    def __init__(self, back: Callable) -> None:
        image: VImage = VImage("assets/images/pac-man-logo.png", size=(289 * 2, 70 * 2))
        image.padding['bottom'] = 35
        players: list[VText] = []
        for index, record in enumerate([("iandalou", 2100), ("andaloui", 900), ("ismaila", 800)]):
            player, score = record
            text: VText = VText(f"{index + 1}. {player} - {score} pts")
            text.padding.update({'top': 7, 'bottom': 7})
            players.append(text)
        Scene.__init__(self,
            VContainer(
                [
                    image,
                    *players,
                    VSelect([
                        VOption("Back", onselect=lambda: back()),
                    ], position=(0, 35), inline=True)
                ],
                fullscreen=True
            )
        )
