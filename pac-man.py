import sys
from time import time
from src.exceptions import ParsingException
from src.parsing import Configuration, Leaderboard
from src.visualizer import Visualizer
from src.playground import Gameplay
from src.screens import MainScreen, GameplayScreen, PauseScreen, LeaderboardScreen, SaveScoreScreen, InstructionScreen


class Pacman:
    def __init__(self) -> None:
        Configuration.loadJSONFile(sys.argv[1])
        Leaderboard.loadJSONFile(Configuration.get('highscore_filename', 'highscore.json'))
        self.visual: Visualizer = Visualizer()
        self.gameplay: Gameplay = Gameplay()

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
        self.gameplay.states.update({
            'level': 1,
            'score': 0,
            'hearts': Configuration.get('lives', 3),
            'expired_at': time() + Configuration.get('level_max_time', 60),
        })
        self.gameplay.onGameWin = self.win
        self.gameplay.onGameLose = self.lose
        self.gameplay.build()
        self.visual.clear()
        self.visual.scenes.append(
            GameplayScreen(self.gameplay, pause=self.pause)
        )

    def leaderboard(self) -> None:
        self.visual.clear()
        self.visual.scenes.append(
            LeaderboardScreen(back=self.launch)
        )

    def instructions(self) -> None:
        self.visual.clear()
        self.visual.scenes.append(
            InstructionScreen(back=self.launch)
        )

    def win(self) -> None:
        self.visual.clear()
        self.visual.scenes.append(
            SaveScoreScreen(
                "Congratulation, You win!",
                self.gameplay.states.get('score'),
                confirm=self.leaderboard,
            )
        )

    def lose(self) -> None:
        self.visual.clear()
        self.visual.scenes.append(
            SaveScoreScreen(
                "You lose :(",
                self.gameplay.states.get('score'),
                confirm=self.leaderboard,
            )
        )

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
        platform.launch()
        platform.visual.render()
    except ParsingException as exception:
        print(exception)
        sys.exit(1)
