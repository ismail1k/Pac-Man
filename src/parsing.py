import json
from typing import Any
from .exceptions import ParsingException


class Configuration:
    def __init__(self) -> None:
        self.data: Any = None

    def loadJSONFile(self, filename: str) -> None:
        try:
            with open(filename, 'r') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            raise ParsingException(f"Fail to load file '{filename}'")
        except json.decoder.JSONDecodeError:
            raise ParsingException(f"File '{filename}' not valid JSON")

    def validate(self) -> None:
        pass

    def get(self, key: str, default: Any = None) -> Any:
        pass
