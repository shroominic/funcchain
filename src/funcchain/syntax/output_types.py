import json
import re
from typing import Optional

from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import BaseLLMOutputParser
from pydantic import BaseModel, Field
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


class CodeBlock(ParserBaseModel):
    code: str
    language: Optional[str] = None

    @classmethod
    def parse(cls, text: str) -> "CodeBlock":
        matches = re.finditer(r"```(?P<language>\w+)?\n?(?P<code>.*?)```", text, re.DOTALL)
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

    @staticmethod
    def custom_grammar() -> str | None:
        return 'root ::= "```" ([^`] | "`" [^`] | "``" [^`])* "```"'

    def __str__(self) -> str:
        return self.code


class Error(BaseModel):
    """
    Fallback function for invalid input.
    If you are unsure on what function to call, use this error function as fallback.
    This will tell the user that the input is not valid.
    """

    title: str = Field(description="CamelCase Name titeling the error")
    description: str = Field(..., description="Short description of the unexpected situation")

    def __raise__(self) -> None:
        raise Exception(self.description)
