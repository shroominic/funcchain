from typing import Any

from langchain_core.exceptions import OutputParserException
from langchain_core.messages import BaseMessage


class ParsingRetryException(OutputParserException):
    """Exception raised when parsing fails."""

    def __init__(self, *args: Any, message: BaseMessage, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.message = message
