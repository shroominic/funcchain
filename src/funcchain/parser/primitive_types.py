"""
Primitive Types Parser
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, create_model

from ..schema.types import UniversalChatModel
from .json_schema import RetryJsonPydanticParser

M = TypeVar("M", bound=BaseModel)


class RetryJsonPrimitiveTypeParser(RetryJsonPydanticParser, Generic[M]):
    """
    Parse primitve types by wrapping them in a PydanticModel and parsing them.
    Examples: int, float, bool, list[str], dict[str, int], Literal["a", "b", "c"], etc.
    """

    def __init__(
        self,
        primitive_type: type,
        retry: int = 1,
        retry_llm: UniversalChatModel = None,
    ) -> None:
        super().__init__(
            pydantic_object=create_model("Extract", value=(primitive_type, ...)),
            retry=retry,
            retry_llm=retry_llm,
        )

    def parse(self, text: str) -> M:
        return super().parse(text).value

    def get_format_instructions(self) -> str:
        """TODO: override with optimized version"""
        return super().get_format_instructions()
