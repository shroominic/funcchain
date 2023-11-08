import re
from typing import Optional

from langchain.pydantic_v1 import BaseModel, Field
from langchain.schema import OutputParserException

from .parser import ParserBaseModel

# PARSER TYPES


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


class Error(BaseModel):
    """If anything goes wrong and you can not do what is expected, use this error function as fallback."""

    title: str = Field(..., description="CamelCase Name titeling the error")
    description: str = Field(..., description="Short description of the unexpected situation")
