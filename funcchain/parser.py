import json
import re
from typing import Callable, Optional, Type, TypeVar

from langchain.output_parsers.format_instructions import PYDANTIC_FORMAT_INSTRUCTIONS
from langchain.pydantic_v1 import BaseModel, ValidationError
from langchain.schema import BaseOutputParser, OutputParserException
from typing_extensions import Self

T = TypeVar("T")


class LambdaOutputParser(BaseOutputParser[T]):
    _parse: Optional[Callable[[str], T]] = None

    def parse(self, text: str) -> T:
        if self._parse is None:
            raise NotImplementedError(
                "LambdaOutputParser.lambda_parse() is not implemented"
            )
        return self._parse(text)

    @property
    def _type(self) -> str:
        return "lambda"


class BoolOutputParser(BaseOutputParser[bool]):
    def parse(self, text: str) -> bool:
        return text.strip()[:1].lower() == "y"

    def get_format_instructions(self) -> str:
        return "\nAnswer only with 'Yes' or 'No'."

    @property
    def _type(self) -> str:
        return "bool"


class MultiToolParser(BaseOutputParser[T]):
    output_types: list[Type[BaseModel]]
    
    def parse(self, function_call: str) -> T:
        obj = None #  parse_openai_function_call(function_call, self.output_types)
        return obj


class ParserBaseModel(BaseModel):
    @classmethod
    def output_parser(cls) -> BaseOutputParser[Self]:  # type: ignore
        return CustomPydanticOutputParser(pydantic_object=cls)

    @classmethod
    def parse(cls, text: str) -> Self:  # type: ignore
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


P = TypeVar("P", bound=ParserBaseModel)


class CustomPydanticOutputParser(BaseOutputParser[P]):
    pydantic_object: Type[P]

    def parse(self, text: str) -> P:
        try:
            return self.pydantic_object.parse(text)
        except (json.JSONDecodeError, ValidationError) as e:
            raise OutputParserException(
                f"Failed to parse {self.pydantic_object.__name__} from completion {text}. Got: {e}",
                llm_output=text,
            )

    def get_format_instructions(self) -> str:
        reduced_schema = self.pydantic_object.schema()
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


class CodeBlock(ParserBaseModel):
    code: str
    language: str = ""

    @classmethod
    def parse(cls, text: str) -> "CodeBlock":
        matches = re.finditer(
            r"```(?P<language>\w+)?\n?(?P<code>.*?)```", text, re.DOTALL
        )
        for match in matches:
            groupdict = match.groupdict()
            groupdict["language"] = groupdict.get("language", "")

            # custom markdown fix
            if groupdict["language"] == "markdown":
                t = text.split("```markdown")[1]
                return cls(
                    language="markdown",
                    code=t[: -(len(t.split("```")[-1]) + 3)],
                )

            return cls(**groupdict)
        raise OutputParserException("Invalid codeblock")

    @staticmethod
    def format_instructions() -> str:
        return "\nAnswer with a codeblock."

    def __str__(self) -> str:
        return self.code
