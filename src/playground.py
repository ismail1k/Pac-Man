from random import random
from time import time, sleep
from typing import Callable
from src.parsing import Configuration
from src.visualizer import Visualizer
from src.interface import VContainer
from src.objects import Canvas, Player, Ghost, Reward, Cheat
from src.helpers import Audio


class Gameplay(VContainer):
    def __init__(self) -> None:
        VContainer.__init__(self, [])
        self.onGameWin: Callable = lambda: None
        self.onGameLose: Callable = lambda: None
        self.absolute: bool = True
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
            self.onGameWin()
        self.states.update({
            'level': level + 1,
            'expired_at': time() + Configuration.get('level_max_time', 60)
        })
        self.build()

    def onPlayerEaten(self, player: Player, opponent: Ghost) -> None:
        if opponent.scared_at + 15 > time():
            cooldown: int = int(abs(time() - opponent.scared_at - 15))
            self.states.update({'score': self.states.get('score') +
                                Configuration.get('points_per_ghost', 100)})
            opponent.dispawn()
            opponent.spawn(*opponent.init_cell, cooldown)
            return None
        if Cheat.invincibility:
            return None
        self.states.update({'hearts': self.states.get('hearts') - 1})
        self.states.update({'freeze': True})
        if self.states.get('hearts') <= 0:
            return self.onGameWin()
        sleep(1.5)
        self.states.update({'freeze': False})
        player.spawn()
        opponent.spawn(*opponent.init_cell)

    def onPlayerClaimReward(self, player: Player, reward: Reward) -> None:
        score: int = Configuration.get('points_per_pacgum', 5)
        if reward.special:
            score = Configuration.get('points_per_super_pacgum', 25)
            Audio.coin()
            for opponent in self.opponents:
                opponent.scared_at = time()
        self.states.update({'score': self.states.get('score') + score})

    def build(self) -> None:
        self.canvas.generate(
            size=(
                Configuration.get('width', 18),
                Configuration.get('height', 12)
            ),
            seed=Configuration.get('seed', random()) + self.states.get('level', 1)
        )
        self.opponents.clear()
        for index, cell in enumerate([(0, 0), (-1, 0), (0, -1), (-1, -1)]):
            opponent: Ghost = Ghost(self.canvas, self.states)
            opponent.type = index
            opponent.player = self.player
            opponent.reset()
            opponent.spawn(*cell)
            opponent.init_cell = cell
            self.opponents.append(opponent)
        rows = len(self.canvas.maze)
        cols = len(self.canvas.maze[0])
        self.rewards.clear()
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
        self.player.spawn()
        self.elements = [self.canvas, *self.rewards, *self.opponents, self.player]
        self.adjust()

    def render(self, visual: Visualizer) -> None:
        if self.states.get('expired_at', time() - 1) <= time():
            self.onGameLose()
        self.canvas.render(visual)
        rect_p = self.player.surface.get_rect(topleft=self.player.position)
        for index, reward in enumerate(self.rewards[:]):
            reward.render(visual)
            rect_r = reward.surface.get_rect(topleft=reward.position)
            if rect_r.colliderect(rect_p):
                self.onPlayerClaimReward(self.player, reward)
                self.rewards.pop(index)
        for opponent in self.opponents:
            opponent.render(visual)
            rect_o = opponent.surface.get_rect(topleft=opponent.position)
            if rect_o.colliderect(rect_p):
                self.onPlayerEaten(self.player, opponent)
        if not len(self.rewards):
            self.onGameLevelUp()
        self.player.render(visual)
