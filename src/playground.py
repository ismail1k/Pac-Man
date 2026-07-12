import pygame
from time import time, sleep
from src.parsing import Configuration
from src.visualizer import Visualizer
from src.interface import VContainer, VImage, VText
from src.objects import Canvas, Player, Ghost, Reward


class Gameplay(VContainer):
    def __init__(self, config: Configuration) -> None:
        VContainer.__init__(self, [])
        self.onGameEnd: Callable = lambda: None
        self.absolute: bool = True
        self.config: Configuration = config
        self.opponents: list[Ghost] = []
        self.rewards: list[Reward] = []
        self.states: dict = {}
        self.canvas = Canvas()
        self.player = Player(
            canvas=self.canvas,
            states=self.states,
        )

    def onGameLevelUp(self) -> None:
        level: int = self.states.get('level')
        if level >= 10:
            self.onGameEnd()
        self.states.update({'level': level + 1})
        self.states.update({'expired_at': time() + 90})

    def onPlayerEaten(self, player: Player, opponent: Ghost) -> None:
        self.states.update({'hearts': self.states.get('hearts') - 1})
        self.states.update({'freeze': True})
        if self.states.get('hearts') <= 0:
            return self.onGameEnd()
        sleep(1.5)
        self.states.update({'freeze': False})
        player.spawn(8, 7)
        opponent.spawn(*opponent.init_cell)

    def reset(self) -> None:
        self.canvas.generate((18, 12))
        self.opponents = []
        for index, cell in enumerate([(0, 0), (-1, 0), (0, -1), (-1, -1)]):
            opponent: Ghost = Ghost(self.canvas, self.states)
            opponent.type = index
            opponent.reset()
            opponent.spawn(*cell)
            opponent.init_cell = cell
            self.opponents.append(opponent)
        self.rewards.clear()
        rows = len(self.canvas.maze)
        cols = len(self.canvas.maze[0])
        for y in range(rows):
            for x in range(cols):
                if self.canvas.maze[y][x] == 15:
                    continue
                special: bool = False
                if (x, y) in [(0, 0), (cols - 1, rows - 1)]:
                    special = True
                if (x, y) in [(cols - 1, 0), (0, rows - 1)]:
                    special = True
                reward: Reward = Reward(self.canvas, special=special)
                reward.spawn(x, y)
                self.rewards.append(reward)
        self.player.reset()
        self.player.spawn(8, 7)
        self.states.update({
            'level': 1,
            'score': 0,
            'hearts': 3,
            'expired_at': time() + 90,
        })
        self.elements = [self.canvas, *self.rewards, *self.opponents, self.player]
        self.adjust()

    def render(self, visual: Visualizer) -> None:
        if self.states.get('expired_at', time() - 1) <= time():
            self.onGameEnd()
        self.canvas.render(visual)
        rect_p = self.player.surface.get_rect(topleft=self.player.position)
        for index, reward in enumerate(self.rewards[:]):
            reward.render(visual)
            rect_r = reward.surface.get_rect(topleft=reward.position)
            if rect_r.colliderect(rect_p):
                reward.onPlayerClaimReward(self.player)
                self.rewards.pop(index)
        for opponent in self.opponents:
            opponent.render(visual)
            rect_o = opponent.surface.get_rect(topleft=opponent.position)
            if rect_o.colliderect(rect_p):
                self.onPlayerEaten(self.player, opponent)
        if not len(self.rewards):
            self.onGameLevelUp()
        self.player.render(visual)
