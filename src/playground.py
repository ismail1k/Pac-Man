import pygame
from src.parsing import Configuration
from src.visualizer import Visualizer
from src.interface import VContainer, VImage, VText
from src.objects import Canvas, Player, Ghost, Reward


class Gameplay(VContainer):
    def __init__(self, config: Configuration) -> None:
        VContainer.__init__(self, [])
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
            'score': 0,
            'hearts': 3,
        })
        self.elements = [self.canvas, *self.rewards, *self.opponents, self.player]
        self.adjust()

    def render(self, visual: Visualizer) -> None:
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
                opponent.onPlayerEaten(self.player)
        self.player.render(visual)
