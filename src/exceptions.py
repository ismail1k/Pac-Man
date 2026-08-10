"""
Custom exceptions used for parsing and runtime errors.
"""


class ParsingException(Exception):
    """Exception raised when a parsing error occurs."""

    def __init__(self, message: str):
        """Initialize the exception with a parsing error message."""
        super().__init__(f"\033[31mParsing:\033[0m {message}")


class RuntimeException(Exception):
    """Exception raised when a runtime error occurs."""

    def __init__(self, message: str):
        """Initialize the exception with a runtime error message."""
        super().__init__(f"\033[31mRuntime:\033[0m {message}")
