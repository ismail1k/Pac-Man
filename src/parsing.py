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
        Configuration.validate_data()

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Return a configuration value or its default value."""
        return Configuration._data.get(key, default)

    @staticmethod
    def validate_data() -> None:
        """
        Validate and sanitize the loaded configuration data in place.
        """
        data = Configuration._data

        # key -> (default, min, max)
        int_fields: dict[str, tuple[int, int, int]] = {
            "width": (15, 5, 30),
            "height": (10, 5, 15),
            "lives": (3, 1, 20),
            "points_per_pacgum": (10, 1, 100),
            "points_per_super_pacgum": (50, 1, 100),
            "points_per_ghost": (200, 1, 1000),
            "level_max_time": (60, 10, 300),
        }

        for key, (default, lo, hi) in int_fields.items():
            value = data.get(key)

            if value is None:
                print(f"Warning: '{key}' is missing, "
                      f"using default {default}.")
                value = default
            elif not isinstance(value, int) or isinstance(value, bool):
                print(f"Warning: '{key}' should be an integer, "
                      f"using default {default}.")
                value = default
            elif value < lo or value > hi:
                print(f"Warning: '{key}'={value} is out of range "
                      f"[{lo}, {hi}], using default {default}.")
                value = default

            data[key] = value

        pacgum_max = max(data["width"] * data["height"] - 18, 1)
        pacgum = data.get("pacgum")

        if pacgum is None:
            print(f"Warning: 'pacgum' is missing, "
                  f"using default {pacgum_max}.")
            pacgum = pacgum_max
        elif not isinstance(pacgum, int) or isinstance(pacgum, bool):
            print(f"Warning: 'pacgum' should be an integer, "
                  f"using default {pacgum_max}.")
            pacgum = pacgum_max
        elif pacgum < 1 or pacgum > pacgum_max:
            print(f"Warning: 'pacgum'={pacgum} is out of range "
                  f"[1, {pacgum_max}], using default {pacgum_max}.")
            pacgum = pacgum_max

        data["pacgum"] = pacgum

        # highscore_filename: non-empty string ending in .json
        default_filename = "highscore.json"
        filename = data.get("highscore_filename")

        if filename is None:
            print(f"Warning: 'highscore_filename' is missing, "
                  f"using default '{default_filename}'.")
            filename = default_filename
        elif not isinstance(filename, str) or not filename.strip():
            print(f"Warning: 'highscore_filename' should be a "
                  f"non-empty string, using default "
                  f"'{default_filename}'.")
            filename = default_filename
        elif not filename.endswith(".json"):
            print(f"Warning: 'highscore_filename' must end with "
                  f"'.json', using default '{default_filename}'.")
            filename = default_filename
        data["highscore_filename"] = filename

        seed = data.get("seed")
        if seed is not None and (
                not isinstance(seed, int) or isinstance(seed, bool)):
            print("Warning: 'seed' should be an integer, ignoring it "
                  "(a random seed will be used).")
            seed = None

        if seed is not None:
            data["seed"] = seed


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
        ))[:10]

    @staticmethod
    def update(name: str, score: int) -> None:
        """Update a player's score and save the leaderboard."""
        Leaderboard._data.update({name: score})
        Utils.save(
            Configuration.get('highscore_filename', 'highscore.json'),
            json.dumps(Leaderboard._data)
        )
