import sys
from src.exceptions import ParsingException
from src.parsing import Configuration
from src.visualizer import Visualizer
from src.helpers import Controller
from src.interface import VContainer, VImage, VText, VSelect, VOption
from src.screens import GameplayScreen, PauseScreen
from src.playground import Gameplay


class Pacman:
    def __init__(self) -> None:
        self.config: Configuration = Configuration()
        self.config.loadJSONFile(sys.argv[1])
        self.config.validate()
        self.controller: Controller = Controller(self.config)
        self.visual: Visualizer = Visualizer(self.config)
        self.states: dict = {}

    def visualize(self) -> None:
        self.visual.controller = self.controller
        self.visual.render()

    def main(self) -> None:
        self.visual.clear()
        self.visual.scenes.append(
            VContainer([
                VImage("assets/images/pac-man-logo.png", size=(289 * 2, 70 * 2)),
                VSelect([
                    VOption("1 Start Game", onselect=(self.launch, ())),
                    VOption("2 View Highscores", onselect=(print, ("2"))),
                    VOption("3 Instructions", onselect=(print, ("3"))),
                    VOption("4 Exit", onselect=(sys.exit, (0,))),
                ], position=(35, 20), controller=self.controller)
            ], fullscreen=True)
        )

    def launch(self) -> None:
        gameplay: Gameplay = Gameplay(
            controller=self.controller,
            events={
                'OnGameplayEnd': (self.main, ())
            }
        )
        pause: Screen = PauseScreen(states=gameplay.states)
        pause.control(self.controller)
        self.visual.clear()
        self.visual.scenes.append(
            GameplayScreen(gameplay)
        )
        # self.visual.scenes.append(pause)


if __name__ == '__main__':
    try:
        # sys.setrecursionlimit(8000)
        platform = Pacman()
        platform.main()
        platform.visualize()
    except ParsingException as exception:
        print(exception)
        sys.exit(1)
