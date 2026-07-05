import pygame
from mazegenerator import MazeGenerator
from src.helpers import Controller
from src.objects import Canvas, Player, Ghost, Reward
from src.visualizer import Visualizer, Widget
from src.interface import VContainer, VImage, VText


class Gameplay(Widget):
    events: dict = {
        'OnGameplayEnd': (print, ("game end!",)),
        'OnPlayerWin': (print, ("You lose :(",)),
        'OnPlayerLose': (print, ("You lose :(",)),
        'OnPlayerLoseHeart': (print, ("Lost heart",)),
    }
    def __init__(self, controller: Controller, events: dict = {}) -> None:
        Widget.__init__(self, pygame.Surface((0, 0)))
        generator = MazeGenerator((18, 12))
        generator.generate()
        self.controller: Controller = controller
        self.states: dict = {
            'pause': False,
            'freeze': False,
            'score': 0,
            'hearts': 3,
        }
        self.visible = lambda: not self.states.get('pause')
        self.events.update(events)
        self.canvas: Canvas = Canvas(
            generator.maze,
            states=self.states,
        )
        self.size = self.canvas.size
        self.player: Player = Player(
            canvas=self.canvas,
            states=self.states,
        )
        self.player.spawn(8, 7)
        self.player.control(self.controller)
        self.opponents: list[Ghost] = []
        for index, cell in enumerate([(0, 0), (-1, 0), (0, -1), (8, 5)]):
            opponent = Ghost(
                canvas=self.canvas,
                states=self.states,
            )
            opponent.type = index
            opponent.spawn(*cell)
            self.opponents.append(opponent)
        self.rewards: list[Reward] = []
        rows = len(self.canvas.maze)
        cols = len(self.canvas.maze[0])
        for y in range(rows):
            for x in range(cols):
                if self.canvas.maze[y][x] == 15:
                    continue
                special: bool = False
                if (x, y) in [(1, 1), (cols - 1, rows - 1)]:
                    special = True
                reward: Reward = Reward(self.canvas, special=special)
                reward.spawn(x, y)
                self.rewards.append(reward)

    def render(self, visual: Visualizer) -> None:
        container_left, container_top = self.position
        self.canvas.offset = self.position
        self.canvas.render(visual)
        rect_p = self.player.surface.get_rect(topleft=self.player.position)
        for index, reward in enumerate(self.rewards[:]):
            reward.offset = self.position
            reward.render(visual)
            rect_r = reward.surface.get_rect(topleft=reward.position)
            if rect_r.colliderect(rect_p):
                reward.OnPlayerClaimReward(self.player)
                self.rewards.pop(index)
        for opponent in self.opponents:
            opponent.offset = self.position
            opponent.render(visual)
            rect_o = opponent.surface.get_rect(topleft=opponent.position)
            if rect_o.colliderect(rect_p):
                opponent.OnPlayerEaten(self.player)
        self.player.offset = self.position
        self.player.render(visual)
