import json
from typing import Any
from src.exceptions import ParsingException
from src.helpers import Utils


class Configuration:
    _data: dict = {}

    @staticmethod
    def loadJSONFile(filename: str) -> None:
        try:
            with open(filename, 'r') as file:
                content: str = ""
                for line in file.readlines():
                    line = line.strip()
                    if not line.startswith('#') and not line.startswith('//'):
                        content += line
                Configuration._data = json.loads(content)
        except FileNotFoundError:
            raise ParsingException(f"Fail to load file '{filename}'")
        except json.decoder.JSONDecodeError:
            raise ParsingException(f"File '{filename}' not valid JSON")

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        return Configuration._data.get(key, default)


class Leaderboard:
    _data: list = []

    @staticmethod
    def loadJSONFile(filename: str) -> None:
        try:
            with open(filename, 'r') as file:
                content: str = ""
                for line in file.readlines():
                    line = line.strip()
                    if not line.startswith('#') and not line.startswith('//'):
                        content += line
                Leaderboard._data = json.loads(content)
        except FileNotFoundError:
            Utils.touch(filename, "{}")
        except json.decoder.JSONDecodeError:
            raise ParsingException(f"File '{filename}' not valid JSON")

    @staticmethod
    def highscores() -> list:
        items: list[dict] = []
        for key, value in Leaderboard._data.items():
            items.append({'player': key, 'score': value})
        return list(sorted(
            items,
            key=lambda r: r['score'],
            reverse=True
        ))

    @staticmethod
    def update(name: str, score: int) -> None:
        Leaderboard._data.update({name: score})
        Utils.save(
            Configuration.get('highscore_filename', 'highscore.json'),
            json.dumps(Leaderboard._data)
        )
