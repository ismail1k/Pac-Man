class ParsingException(Exception):
    def __init__(self, message: str):
        super().__init__(f"\033[31mParsing:\033[0m {message}")


class RuntimeException(Exception):
    def __init__(self, message: str):
        super().__init__(f"\033[31mRuntime:\033[0m {message}")
