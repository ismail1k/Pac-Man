"""Configuration and leaderboard management utilities."""
import json
from typing import Any
from src.exceptions import ParsingException
from src.helpers import Utils


class Configuration:
    """Manages application configuration loaded from a JSON file."""

    _data: dict = {}

    @staticmethod
    def loadJSONFile(filename: str) -> None:
        """Load configuration data from a JSON file."""
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
        """Return a configuration value or its default value."""
        return Configuration._data.get(key, default)


class Leaderboard:
    """Manages player scores loaded from and saved to a JSON file."""

    _data: dict = {}

    @staticmethod
    def loadJSONFile(filename: str) -> None:
        """Load leaderboard data from a JSON file."""
        try:
            with open(filename, 'r') as file:
                content: str = ""
                for line in file.readlines():
                    line = line.strip()
                    if not line.startswith('#') and not line.startswith('//'):
                        content += line
                Leaderboard._data = json.loads(content)
        except FileNotFoundError:
            Utils.save(filename, "{}")
        except json.decoder.JSONDecodeError:
            raise ParsingException(f"File '{filename}' not valid JSON")

    @staticmethod
    def highscores() -> list:
        """Return leaderboard scores sorted from highest to lowest."""
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
        """Update a player's score and save the leaderboard."""
        Leaderboard._data.update({name: score})
        Utils.save(
            Configuration.get('highscore_filename', 'highscore.json'),
            json.dumps(Leaderboard._data)
        )
