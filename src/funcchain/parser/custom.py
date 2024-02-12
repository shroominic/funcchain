import json
import re
from typing import Type, TypeVar

from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import BaseLLMOutputParser, BaseOutputParser
from pydantic import BaseModel, ValidationError
from typing_extensions import Self


class ParserBaseModel(BaseModel):
    @classmethod
    def output_parser(cls) -> BaseLLMOutputParser[Self]:
        from ..parser.custom import CustomPydanticOutputParser

        return CustomPydanticOutputParser(pydantic_object=cls)

    @classmethod
    def parse(cls, text: str) -> Self:
        """Override for custom parsing."""
        match = re.search(r"\{.*\}", text.strip(), re.MULTILINE | re.IGNORECASE | re.DOTALL)
        json_str = ""
        if match:
            json_str = match.group()
        json_object = json.loads(json_str, strict=False)
        return cls.model_validate(json_object)

    @staticmethod
    def format_instructions() -> str:
        return (
            "Please respond with a json result matching the following schema:"
            "\n\n```schema\n{schema}\n```\n"
            "Do not repeat the schema. Only respond with the result."
        )

    @staticmethod
    def custom_grammar() -> str | None:
        return None


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
