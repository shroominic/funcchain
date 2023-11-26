import re
import copy
import json
from typing import Callable, Optional, Type, TypeVar

from langchain.schema import (
    ChatGeneration,
    Generation,
    OutputParserException,
    AIMessage,
)
from langchain.output_parsers.format_instructions import PYDANTIC_FORMAT_INSTRUCTIONS
from langchain.schema.output_parser import BaseGenerationOutputParser, BaseOutputParser
from pydantic import BaseModel, ValidationError

from .types import ParserBaseModel, CodeBlock as CodeBlock
from .exceptions import ParsingRetryException

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


M = TypeVar("M", bound=BaseModel)


class PydanticFuncParser(BaseGenerationOutputParser[M]):
    pydantic_schema: Type[M]
    args_only: bool = False

    def parse_result(self, result: list[Generation], *, partial: bool = False) -> M:
        generation = result[0]
        if not isinstance(generation, ChatGeneration):
            raise OutputParserException(
                "This output parser can only be used with a chat generation.",
            )
        message = generation.message
        try:
            func_call = copy.deepcopy(message.additional_kwargs["function_call"])
        except KeyError as exc:
            raise ParsingRetryException(
                f"Could not parse function call: {exc}",
                message=message,
            )

        if self.args_only:
            _result = func_call["arguments"]
        else:
            _result = func_call
        try:
            if self.args_only:
                pydantic_args = self.pydantic_schema.model_validate_json(_result)
            else:
                pydantic_args = self.pydantic_schema.model_validate_json(
                    _result["arguments"]
                )
        except ValidationError as exc:
            raise ParsingRetryException(
                f"Could not parse function call: {exc}", message=message
            )
        return pydantic_args


class MultiToolParser(BaseGenerationOutputParser[M]):
    output_types: list[Type[M]]
    args_only: bool = False

    def parse_result(self, result: list[Generation], *, partial: bool = False) -> M:
        function_call = self._pre_parse_function_call(result)

        output_type_names = [t.__name__.lower() for t in self.output_types]

        if function_call["name"] not in output_type_names:
            raise OutputParserException("Invalid function call")

        print(function_call["name"])

        output_type = self._get_output_type(function_call["name"])

        generation = result[0]
        if not isinstance(generation, ChatGeneration):
            raise OutputParserException(
                "This output parser can only be used with a chat generation."
            )
        message = generation.message
        try:
            func_call = copy.deepcopy(message.additional_kwargs["function_call"])
        except KeyError as exc:
            raise ParsingRetryException(
                f"Could not parse function call: {exc}", message=message
            )

        if self.args_only:
            _result = func_call["arguments"]
        else:
            _result = func_call

        try:
            if self.args_only:
                pydantic_args = output_type.model_validate_json(_result)
            else:
                pydantic_args = output_type.model_validate_json(_result["arguments"])
        except ValidationError as exc:
            raise ParsingRetryException(
                f"Could not parse function call: {exc}",
                message=message,
            )
        return pydantic_args

    def _pre_parse_function_call(self, result: list[Generation]) -> dict:
        generation = result[0]
        if not isinstance(generation, ChatGeneration):
            raise OutputParserException(
                "This output parser can only be used with a chat generation."
            )
        message = generation.message
        try:
            func_call = copy.deepcopy(message.additional_kwargs["function_call"])
        except KeyError:
            raise ParsingRetryException(
                f"The model refused to respond with a function call:\n{message.content}\n\n",
                message=message,
            )

        return func_call

    def _get_output_type(self, function_name: str) -> Type[M]:
        output_type_iter = filter(
            lambda t: t.__name__.lower() == function_name, self.output_types
        )
        if output_type_iter is None:
            raise OutputParserException(
                f"No parser found for function: {function_name}"
            )
        return next(output_type_iter)


P = TypeVar("P", bound=ParserBaseModel)


class CustomPydanticOutputParser(BaseOutputParser[P]):
    pydantic_object: Type[P]

    def parse(self, text: str) -> P:
        try:
            return self.pydantic_object.parse(text)
        except (json.JSONDecodeError, ValidationError) as e:
            raise ParsingRetryException(
                f"Failed to parse {self.pydantic_object.__name__} from completion {text}. Got: {e}",
                message=AIMessage(content=text),
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


class PydanticOutputParser(BaseOutputParser[M]):
    """Parse an output using a pydantic model."""

    pydantic_object: Type[M]
    """The pydantic model to parse."""

    def parse(self, text: str) -> M:
        try:
            # Greedy search for 1st json candidate.
            match = re.search(
                r"\{.*\}", text.strip(), re.MULTILINE | re.IGNORECASE | re.DOTALL
            )
            json_str = ""
            if match:
                json_str = match.group()
            json_object = json.loads(json_str, strict=False)
            return self.pydantic_object.model_validate(json_object)

        except (json.JSONDecodeError, ValidationError) as e:
            raise ParsingRetryException(
                str(e),
                message=AIMessage(content=text),
            )

    def get_format_instructions(self) -> str:
        schema = self.pydantic_object.model_json_schema()

        # Remove extraneous fields.
        reduced_schema = schema
        if "title" in reduced_schema:
            del reduced_schema["title"]
        if "type" in reduced_schema:
            del reduced_schema["type"]
        # Ensure json in context is well-formed with double quotes.
        schema_str = json.dumps(reduced_schema)

        return PYDANTIC_FORMAT_INSTRUCTIONS.format(schema=schema_str)

    @property
    def _type(self) -> str:
        return "pydantic"
