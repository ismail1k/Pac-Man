import pygame
from threading import Thread
from typing import Any, Callable
from src.parsing import Configuration


class Controller:
    ACTION_UP = [pygame.K_UP, pygame.K_w]
    ACTION_DOWN = [pygame.K_DOWN, pygame.K_s]
    ACTION_LEFT = [pygame.K_LEFT, pygame.K_a]
    ACTION_RIGHT = [pygame.K_RIGHT, pygame.K_d]
    ACTION_PAUSE = [pygame.K_p]
    ACTION_CONFIRM = [pygame.K_RETURN, 0]
    ACTION_BACK = [pygame.K_BACKSPACE, 1]
    ACTION_QUIT = [pygame.K_ESCAPE, pygame.K_q]
    def __init__(self, config: Configuration) -> None:
        self.joysticks: dict = {}
        self.events: list[dict] = []

    def joystick(self, joystick: Any) -> int:
        joystick_id: int = joystick.get_instance_id()
        joystick_name: str = joystick.get_name()
        self.joysticks.update({joystick_id: joystick})
        print(f"Controller Connected: {joystick_name} (ID: {joystick_id})")
        return joystick_id

    def onclick(self, actions: list[int], callback: tuple[Callable, tuple]) -> list[int]:
        actions_ids: list[int] = []
        for action in actions:
            identifier = 1
            while identifier <= len(self.events):
                found = False
                for event in self.events:
                    if event['identifier'] == identifier:
                        found = True
                        break
                if not found:
                    break
                identifier += 1
            self.events.append({
                'identifier': identifier,
                'action': action,
                'callback': callback
            })
            actions_ids.append(identifier)
        return actions_ids

    def listen(self, button: int) -> None:
        for event in self.events:
            if event['action'] == button:
                function, args = event['callback']
                function(*args)

    def destroy(self, events: list[int]) -> None:
        self.events = list(filter(lambda e: e['identifier'] not in events, self.events))
