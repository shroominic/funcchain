import re
import json
from typing import Optional, Self

from pydantic.v1 import BaseModel, Field
from langchain.schema import OutputParserException
from langchain.output_parsers.format_instructions import PYDANTIC_FORMAT_INSTRUCTIONS
from langchain.schema.output_parser import BaseOutputParser


class ParserBaseModel(BaseModel):
    @classmethod
    def output_parser(cls) -> BaseOutputParser[Self]:
        from .parser import CustomPydanticOutputParser

        return CustomPydanticOutputParser(pydantic_object=cls)

    @classmethod
    def parse(cls, text: str) -> Self:
        """Override for custom parsing."""
        match = re.search(
            r"\{.*\}", text.strip(), re.MULTILINE | re.IGNORECASE | re.DOTALL
        )
        json_str = ""
        if match:
            json_str = match.group()
        json_object = json.loads(json_str, strict=False)
        return cls.parse_obj(json_object)

    @staticmethod
    def format_instructions() -> str:
        return PYDANTIC_FORMAT_INSTRUCTIONS


class CodeBlock(ParserBaseModel):
    code: str
    language: Optional[str] = None

    @classmethod
    def parse(cls, text: str) -> "CodeBlock":
        matches = re.finditer(
            r"```(?P<language>\w+)?\n?(?P<code>.*?)```", text, re.DOTALL
        )
        for match in matches:
            groupdict = match.groupdict()
            groupdict["language"] = groupdict.get("language", None)

            # custom markdown fix
            if groupdict["language"] == "markdown":
                t = text.split("```markdown")[1]
                return cls(
                    language="markdown",
                    code=t[: -(len(t.split("```")[-1]) + 3)],
                )

            return cls(**groupdict)

        return cls(code=text)  # TODO: fix this hack
        raise OutputParserException("Invalid codeblock")

    @staticmethod
    def format_instructions() -> str:
        return "Answer with a codeblock."

    def __str__(self) -> str:
        return self.code


class Error(BaseModel):
    """
    If anything goes wrong and you can not do what is expected,
    use this error function as fallback.
    """

    title: str = Field(..., description="CamelCase Name titeling the error")
    description: str = Field(
        ..., description="Short description of the unexpected situation"
    )

    def __raise__(self) -> None:
        raise Exception(self.description)
