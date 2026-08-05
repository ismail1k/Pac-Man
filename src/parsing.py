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
                if not isinstance(json.loads(content), list):
                    raise ParsingException(f"file '{filename}' content is not list")
                Leaderboard._data = json.loads(content)
        except FileNotFoundError:
            Utils.touch(filename, "[]")
        except json.decoder.JSONDecodeError:
            raise ParsingException(f"File '{filename}' not valid JSON")


    @staticmethod
    def highscores() -> list:
        return list(sorted(
            Leaderboard._data,
            key=lambda r: r['score'],
            reverse=True
        ))
