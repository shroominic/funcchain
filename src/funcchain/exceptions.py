from typing import Any

from langchain.schema.messages import BaseMessage
from langchain.schema.output_parser import OutputParserException


class ParsingRetryException(OutputParserException):
    """Exception raised when parsing fails."""

    def __init__(self, *args: Any, message: BaseMessage, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.message = message
