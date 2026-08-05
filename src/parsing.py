import json
from typing import Any
from .exceptions import ParsingException


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
