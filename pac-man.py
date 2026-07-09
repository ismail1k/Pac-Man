import sys
from src.exceptions import ParsingException
from src.parsing import Configuration
from src.visualizer import Visualizer
from src.interface import VContainer, VImage, VText, VSelect, VOption
from src.screens import MainScreen, GameplayScreen, PauseScreen
from src.playground import Gameplay


class Pacman:
    def __init__(self) -> None:
        self.config: Configuration = Configuration()
        self.config.loadJSONFile(sys.argv[1])
        self.visual: Visualizer = Visualizer(self.config)
        self.gameplay: Gameplay = Gameplay(self.config)

    def launch(self) -> None:
        self.visual.clear()
        self.visual.scenes.append(
            MainScreen(
                play=self.play,
                leaderboard=self.leaderboard,
                instructions=self.instructions
            )
        )

    def play(self) -> None:
        self.gameplay.reset()
        self.visual.clear()
        self.visual.scenes.append(
            GameplayScreen(self.gameplay, pause=self.pause)
        )

    def leaderboard(self) -> None:
        self.visual.clear()

    def instructions(self) -> None:
        self.visual.clear()

    def pause(self) -> None:
        self.visual.clear()
        self.visual.scenes.append(
            PauseScreen(
                resume=self.resume,
                launch=self.launch,
            )
        )

    def resume(self) -> None:
        self.visual.clear()
        self.visual.scenes.append(
            GameplayScreen(self.gameplay, pause=self.pause)
        )


if __name__ == '__main__':
    try:
        # sys.setrecursionlimit(8000)
        platform = Pacman()
        platform.config.validate()
        platform.launch()
        platform.visual.render()
    except ParsingException as exception:
        print(exception)
        sys.exit(1)
