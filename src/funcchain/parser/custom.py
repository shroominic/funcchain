import json
from typing import Type, TypeVar

from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import BaseOutputParser
from pydantic import ValidationError

from ..syntax.output_types import CodeBlock as CodeBlock
from ..syntax.output_types import ParserBaseModel

P = TypeVar("P", bound=ParserBaseModel)


class CustomPydanticOutputParser(BaseOutputParser[P]):
    pydantic_object: Type[P]

    def parse(self, text: str) -> P:
        try:
            return self.pydantic_object.parse(text)
        except (json.JSONDecodeError, ValidationError) as e:
            raise OutputParserException(
                f"Failed to parse {self.pydantic_object.__name__} " f"from completion {text}. Got: {e}",
                llm_output=text,
            )

    def get_format_instructions(self) -> str:
        reduced_schema = self.pydantic_object.model_json_schema()
        if "title" in reduced_schema:
            del reduced_schema["title"]
        if "type" in reduced_schema:
            del reduced_schema["type"]

        return self.pydantic_object.format_instructions().format(
            schema=json.dumps(reduced_schema),
        )

    @property
    def _type(self) -> str:
        return "pydantic"
