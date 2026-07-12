import pygame, sys
from abc import ABC
from typing import Callable
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
        screen_w, screen_h = Visualizer.resolution
        image: Widget = self.image()
        image.left += (gameplay.width/2) - (image.width/2) - 25
        image.top -= image.height + 10
        score: Widget = self.score()
        score.top -= score.height + 10
        hearts = self.hearts()
        hearts.top = gameplay.height / 2
        Controller.__init__(self)
        self.onClick(self.ACTION_PAUSE, lambda: pause())
        self.gameplay: Gameplay = gameplay
        Scene.__init__(self,
            VContainer(
                [gameplay, score, image, hearts],
                fullscreen=True,
                absolute=True,
            )
        )

    def image(self) -> Widget:
        return VImage("assets/images/pac-man-logo.png")

    def score(self) -> Widget:
        return VText(lambda: f"Score: {self.gameplay.states.get('score')}")

    def hearts(self) -> Widget:
        attempts: list[Widget] = []
        for index in range(3):
            attempts.append(
                VImage(
                    "assets/images/player_open.png", size=(40, 40),
                    visible=lambda: self.gameplay.states.get('hearts') > index
                )
            )
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
            players.append(VText(f"{index + 1}. {player} - {score} pts"))
        Scene.__init__(self,
            VContainer(
                [
                    image,
                    *players,
                    VSelect([
                        VOption("Back", onselect=lambda: sys.exit(0)),
                    ], position=(0, 35), inline=True)
                ],
                fullscreen=True
            )
        )
