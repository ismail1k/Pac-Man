import json
from typing import Any
from .exceptions import ParsingException


class Configuration:
    def __init__(self) -> None:
        self.data: str = ""
        self.json: Any = None
        self._comment: bool = False

    def loadJSONFile(self, filename: str) -> None:
        self._comment = False
        try:
            with open(filename, 'r') as file:
                self.data = file.readlines()
                content = ""
                for line in self.data:
                    content += self._remove_comment(line)
                self.json = json.loads(content)

        except FileNotFoundError:
            raise ParsingException(f"Fail to load file '{filename}'")
        except json.decoder.JSONDecodeError:
            raise ParsingException(f"File '{filename}' not valid JSON")

    def _remove_comment(self, line: str) -> str:
        clean_line = ""
        ch_1 = True
        ch_2 = True
        c_hs = False
        if self._comment:
            c_hs = True
        ln = len(line)
        for i, c in enumerate(line):
            if c == '"':
                ch_1 = not ch_1
            if c == "'":
                ch_2 = not ch_2
            if (ch_1 and ch_2 and c == "/" and ln > i+1 and line[i+1] == "/"):
                self._comment = True
            if ch_1 and ch_2 and c == "#":
                self._comment = True
            if ch_1 and ch_2 and c == "/" and ln > i+1 and line[i+1] == "*":
                self._comment = True
                c_hs = True
            if ch_1 and ch_2 and c == "/" and i and line[i-1] == "*" and c_hs:
                c_hs = False
                self._comment = False
                continue
            if not self._comment:
                clean_line += c
        if not c_hs:
            self._comment = False
        return clean_line.strip()

    def validate(self) -> None:
        pass

    def get(self, key: str, default: Any = None) -> Any:
        return self.json.get(key, default)
