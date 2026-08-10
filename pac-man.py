"""
Run the Pacman game and manage its screens, gameplay, and score flow.
"""

import sys
from time import time

from src.exceptions import ParsingException
from src.parsing import Configuration, Leaderboard
from src.visualizer import Visualizer
from src.playground import Gameplay
from src.screens import (
    MainScreen,
    GameplayScreen,
    PauseScreen,
    LeaderboardScreen,
    SaveScoreScreen,
    InstructionScreen,
)


class Pacman:
    """Manage the Pacman game lifecycle, screens, gameplay, and score flow."""

    def __init__(self) -> None:
        """Load configuration and initialize the visualizer and gameplay."""
        Configuration.loadJSONFile(sys.argv[1])
        Leaderboard.loadJSONFile(
            Configuration.get("highscore_filename", "highscore.json")
        )
        self.visual: Visualizer = Visualizer()
        self.gameplay: Gameplay = Gameplay()
        self.gameplay.onGameWin = self.win
        self.gameplay.onGameLose = self.lose

    def launch(self) -> None:
        """Display the main menu screen."""
        self.visual.clear()
        self.visual.scenes.append(
            MainScreen(
                play=self.play,
                leaderboard=self.leaderboard,
                instructions=self.instructions,
            )
        )

    def play(self) -> None:
        """Initialize a new game and display the gameplay screen."""
        self.gameplay.states.update({
            "level": 1,
            "score": 0,
            "hearts": Configuration.get("lives", 3),
            "expired_at": time() + Configuration.get("level_max_time", 60),
        })
        self.gameplay.build()
        self.visual.clear()
        self.visual.scenes.append(
            GameplayScreen(self.gameplay, pause=self.pause)
        )

    def leaderboard(self) -> None:
        """Display the leaderboard screen."""
        self.visual.clear()
        self.visual.scenes.append(
            LeaderboardScreen(back=self.launch)
        )

    def instructions(self) -> None:
        """Display the game instructions screen."""
        self.visual.clear()
        self.visual.scenes.append(
            InstructionScreen(back=self.launch)
        )

    def win(self) -> None:
        """Display the score-saving screen after winning the game."""
        self.visual.clear()
        self.visual.scenes.append(
            SaveScoreScreen(
                "Congratulation, You win!",
                self.gameplay.states.get("score"),
                confirm=self.leaderboard,
            )
        )

    def lose(self) -> None:
        """Display the score-saving screen after losing the game."""
        self.visual.clear()
        self.visual.scenes.append(
            SaveScoreScreen(
                "You lose :(",
                self.gameplay.states.get("score"),
                confirm=self.leaderboard,
            )
        )

    def pause(self) -> None:
        """Display the pause screen and provide a resume option."""
        self.visual.clear()
        self.visual.scenes.append(
            PauseScreen(
                resume=self.resume,
                launch=self.launch,
            )
        )

    def resume(self) -> None:
        """Resume the current game and display the gameplay screen."""
        self.visual.clear()
        self.visual.scenes.append(
            GameplayScreen(self.gameplay, pause=self.pause)
        )


if __name__ == "__main__":
    try:
        platform = Pacman()
        platform.launch()
        platform.visual.render()
    except ParsingException as exception:
        print(exception)
        sys.exit(1)
