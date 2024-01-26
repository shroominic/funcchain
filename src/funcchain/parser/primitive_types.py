"""
Primitive Types Parser
"""
from typing import Generic, TypeVar

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, create_model

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
        retry_llm: BaseChatModel | str | None = None,
    ) -> None:
        super().__init__(
            pydantic_object=create_model("ExtractPrimitiveType", value=(primitive_type, ...)),
            retry=retry,
            retry_llm=retry_llm,
        )

    def parse(self, text: str) -> M:
        return super().parse(text).value
