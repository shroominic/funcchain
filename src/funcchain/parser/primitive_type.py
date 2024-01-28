from typing import TypeVar

from langchain_core.output_parsers import BaseOutputParser

from ..syntax.output_types import CodeBlock as CodeBlock

T = TypeVar("T")


# TODO: remove and implement primitive type output parser using nested pydantic extraction
class BoolOutputParser(BaseOutputParser[bool]):
    def parse(self, text: str) -> bool:
        return text.strip()[:1].lower() == "y"

    def get_format_instructions(self) -> str:
        return "\nAnswer only with 'Yes' or 'No'."

    @property
    def _type(self) -> str:
        return "bool"
