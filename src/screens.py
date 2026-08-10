"""
UI scene definitions for menus, gameplay HUD, leaderboard, and instructions.
"""

import pygame
import sys
from abc import ABC
from time import time
from typing import Callable
from functools import partial
from src.visualizer import Visualizer
from src.interface import VContainer, VImage, VText, VField, VSelect, VOption
from src.parsing import Configuration, Leaderboard
from src.helpers import Widget, Controller, Audio
from src.playground import Gameplay


class Scene(Widget, ABC):
    """Base scene wrapping a widget tree for rendering."""

    def __init__(self, scene: Widget) -> None:
        """Initialize scene with a root widget."""
        Widget.__init__(self, pygame.Surface(Visualizer.resolution))
        self._scene: Widget = scene

    def render(self, visual: Visualizer) -> None:
        """Render the wrapped scene."""
        self._scene.render(visual)


class MainScreen(Scene):
    """Main menu with logo and navigation options."""

    def __init__(self,
                 play: Callable,
                 leaderboard: Callable,
                 instructions: Callable,
                 ) -> None:
        """Build main menu with play, leaderboard, instructions and exit options."""
        Audio.menu()
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
    """In-game HUD overlay showing score, lives, timer and level."""

    def __init__(self, gameplay: Gameplay, pause: Callable) -> None:
        """Assemble gameplay view with HUD elements and pause binding."""
        Controller.__init__(self)
        self.gameplay: Gameplay = gameplay
        self.onClick(self.ACTION_PAUSE, lambda: pause())
        screen_w, screen_h = Visualizer.resolution
        score: Widget = VText(lambda: f"Score: {self.gameplay.states.get('score')}")
        score.padding.update({'bottom': 10})
        score.top -= score.size[1]
        hearts = self._hearts()
        hearts.top = gameplay.height / 2
        hearts.padding.update({'top': 10})
        timer: VText = VText(lambda: f"{int(self.gameplay.states.get('expired_at', time()) - time())} second(s)")
        timer.top = gameplay.height
        timer.left += gameplay.width - timer.width
        timer.padding.update({'top': 10})
        level: VText = VText(lambda: f"Level: {self.gameplay.states.get('level')}/10")
        level.padding.update({'bottom': 10})
        level.top -= level.size[1]
        level.left += gameplay.width - level.width
        image: Widget = VImage("assets/images/pac-man-logo.png")
        image.left += (gameplay.width/2) - (image.width/2)
        image.padding.update({'bottom': 10})
        image.top -= image.size[1] + level.size[1]
        Audio.music()
        Scene.__init__(self, VContainer(
                [gameplay, score, image, hearts, timer, level],
                fullscreen=True,
                absolute=True,
            )
        )

    def _hearts(self) -> Widget:
        """Return a row of heart icons reflecting remaining lives."""
        attempts: list[Widget] = []
        for index in range(self.gameplay.states.get('hearts', 0)):
            image: VImage = VImage("assets/images/player_open.png", size=(40, 40))
            image.visible = partial(lambda index: self.gameplay.states.get('hearts') > index, index)
            attempts.append(image)
        return VContainer(attempts, inline=True)

    def render(self, visual: Visualizer) -> None:
        """Process controller input and render the gameplay scene."""
        self.listenControllerEvents(visual.events)
        Scene.render(self, visual)


class PauseScreen(Scene):
    """Pause overlay with resume, menu, and exit options."""

    def __init__(self, resume: Callable, launch: Callable) -> None:
        """Build pause menu with resume, main menu and exit choices."""
        Scene.__init__(self, VContainer(
                [
                    VImage("assets/images/pac-man-logo.png", size=(289 * 2, 70 * 2)),
                    VSelect([
                        VOption("1 Continue", onselect=lambda: resume()),
                        VOption("2 Main Menu", onselect=lambda: launch()),
                        VOption("2 Exit", onselect=lambda: sys.exit(0)),
                    ], position=(35, 20))
                ],
                fullscreen=True
            )
        )


class LeaderboardScreen(Scene):
    """High scores display with navigation back to menu."""

    def __init__(self, back: Callable) -> None:
        """Build leaderboard view listing top scores."""
        image: VImage = VImage("assets/images/pac-man-logo.png", size=(289 * 2, 70 * 2))
        image.padding['bottom'] = 35
        players: list[VText] = []
        for index, record in enumerate(Leaderboard.highscores()):
            text: VText = VText(f"{index + 1}. {record['player']} - {record['score']} pts")
            text.padding.update({'top': 7, 'bottom': 7})
            players.append(text)
        if not len(Leaderboard.highscores()):
            players.append(
                VText("Empty leaderboard!")
            )
        Scene.__init__(self, VContainer(
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


class SaveScoreScreen(Scene, Controller):
    """Score entry screen with keyboard input for player name."""

    def __init__(self, label: str, score: int, confirm: Callable) -> None:
        """Build score save screen with text input and confirm action."""
        Controller.__init__(self)
        value: str = ""

        def _add(key) -> None:
            nonlocal value
            if len(value) >= 10:
                return None
            if key == pygame.K_SPACE:
                value = value + " "
            else:
                value = value + pygame.key.name(key)

        def _remove() -> None:
            nonlocal value
            value = value[:-1]

        def _confirm() -> None:
            nonlocal value
            Leaderboard.update(value, score)
            if len(value) > 2:
                confirm()

        self.onClick(self.INPUT_KEYBOARD, _add)
        self.onClick(self.ACTION_BACK, _remove)
        self.onClick(self.ACTION_CONFIRM, _confirm)
        image: VImage = VImage("assets/images/pac-man-logo.png", size=(289 * 2, 70 * 2))
        image.padding.update({'bottom': 40})
        title: VText = VText(label)
        title.padding.update({'bottom': 15})
        summary: VText = VText(f'Your Score: {score} pts')
        summary.padding.update({'bottom': 15})
        description: VText = VText("Put your name bellow")
        description.padding.update({'bottom': 15})
        field: VField = VField(lambda: value)
        field.width = image.size[0] - 40
        Scene.__init__(self, VContainer(
                                [
                                    image,
                                    title,
                                    summary,
                                    description,
                                    field,
                                ],
                                fullscreen=True
            )
        )

    def render(self, visual: Visualizer) -> None:
        """Process keyboard input and render the save score scene."""
        self.listenControllerEvents(visual.events)
        Scene.render(self, visual)


class InstructionScreen(Scene):
    """How-to-play screen showing controls, rules and scoring."""

    def __init__(self, back: Callable):
        """
        Build instructions view with gameplay guide and back button.
        """
        INSTRUCTIONS = [
            "HOW TO PLAY:",
            "",
            "Move your character with the arrows or WASD keys.",
            "",
            "Collect all the pac-gums scattered around the maze to complete "
            "the level. ",
            "Corner pac-gums are special (super pac-gums): eating one turns "
            "the ghosts ",
            "scared for a short time, letting you eat them for bonus points.",
            "",
            "Avoid the ghosts! If a ghost catches you while it isn't scared,"
            " you lose ",
            "a heart and briefly freeze before respawning."
            " Lose all your hearts and ",
            "the game is over.",
            "",
            "Each level has a time limit — clear it before "
            "time runs out or you lose.",
            "Clear all 10 levels to win the game.",
            "",
            "SCORING",
            f"- Pac-gum: {Configuration.get('points_per_pacgum', 5)} points",
            "- Super pac-gum: "
            f"{Configuration.get('points_per_super_pacgum', 25)} points",
            "- Eating a scared ghost: "
            f"{Configuration.get('points_per_ghost', 100)} points",
            "",
            "Good luck!"
        ]
        elements = []
        margin = -80
        for line in INSTRUCTIONS:
            elements.append(VText(line, position=(0, margin)))
            margin += 10
        elements.append(VSelect([VOption("Back", onselect=lambda: back())],
                        position=(0, margin + 40), inline=True))

        super().__init__(VContainer(elements, fullscreen=True))
