"""
Pac-Man game engine with level progression, collision handling, and scoring.
"""

from random import random, shuffle
from time import time, sleep
from typing import Callable
from src.parsing import Configuration
from src.visualizer import Visualizer
from src.interface import VContainer
from src.objects import Canvas, Player, Ghost, Reward
from src.helpers import Audio, Cheat


class Gameplay(VContainer):
    """
    Main game container managing maze, entities, state, and gameplay loop.
    """

    def __init__(self) -> None:
        """Initialize game state, canvas, player, and event callbacks."""
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
        """Advance to next level or trigger win if max level reached."""
        level: int = self.states.get('level')
        if level >= 10:
            self.onGameWin()
        self.states.update({
            'level': level + 1,
            'expired_at': time() + Configuration.get('level_max_time', 60)
        })
        self.build()

    def onPlayerEaten(self, player: Player, opponent: Ghost) -> None:
        """Handle player-ghost collision: eat scared ghost or lose a life."""
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
            return self.onGameLose()
        sleep(1.5)
        self.states.update({'freeze': False})
        player.spawn()
        for opp in self.opponents:
            opp.spawn(*opp.init_cell)

    def onPlayerClaimReward(self, player: Player, reward: Reward) -> None:
        """Process reward collection and update score."""
        score: int = Configuration.get('points_per_pacgum', 5)
        if reward.special:
            score = Configuration.get('points_per_super_pacgum', 25)
            Audio.coin()
            for opponent in self.opponents:
                opponent.scared_at = time()
        self.states.update({'score': self.states.get('score') + score})

    def build(self) -> None:
        """Generate maze, spawn entities, and reset positions for current level."""
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
        positions = []
        for y in range(rows):
            for x in range(cols):
                if self.canvas.maze[y][x] == 15:
                    continue
                special: bool = False
                if (x, y) in [(0, 0), (cols - 1, rows - 1)]:
                    special = True
                if (x, y) in [(cols - 1, 0), (0, rows - 1)]:
                    special = True
                if special is False:
                    positions.append((x, y))
                    continue
                reward: Reward = Reward(self.canvas, special=special)
                reward.spawn(x, y)
                self.rewards.append(reward)
        shuffle(positions)
        for pos in positions[:Configuration.get("pacgum", len(positions))]:
            reward = Reward(self.canvas)
            reward.spawn(*pos)
            self.rewards.append(reward)

        self.player.reset()
        self.player.spawn()
        self.elements = [self.canvas, *self.rewards, *self.opponents, self.player]
        self.adjust()

    def render(self, visual: Visualizer) -> None:
        """
        Execute game frame: apply cheats, check timers,
        render and collide entities.
        """
        if Cheat.level:
            self.onGameLevelUp()
            Cheat.level = False
        if Cheat.extra_lives:
            if self.states["hearts"] < Configuration.get('lives'):
                self.states["hearts"] += 1
            Cheat.extra_lives = False

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
