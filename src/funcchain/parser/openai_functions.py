import copy
from typing import Type, TypeVar

from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import BaseGenerationOutputParser
from langchain_core.outputs import ChatGeneration, Generation
from pydantic import BaseModel, ValidationError

from ..syntax.output_types import CodeBlock as CodeBlock
from ..utils.msg_tools import msg_to_str

M = TypeVar("M", bound=BaseModel)


# TODO: retry wrapper
class OpenAIFunctionPydanticParser(BaseGenerationOutputParser[M]):
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
            raise OutputParserException(
                f"Could not parse function call: {exc}",
                llm_output=msg_to_str(message),
            )

        if self.args_only:
            _result = func_call["arguments"]
        else:
            _result = func_call
        try:
            if self.args_only:
                pydantic_args = self.pydantic_schema.model_validate_json(_result)
            else:
                pydantic_args = self.pydantic_schema.model_validate_json(_result["arguments"])
        except ValidationError as exc:
            raise OutputParserException(
                f"Could not parse function call: {exc}",
                llm_output=msg_to_str(message),
            )
        return pydantic_args


# TODO: retry wrapper
class OpenAIFunctionPydanticUnionParser(BaseGenerationOutputParser[M]):
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
            raise OutputParserException("This output parser can only be used with a chat generation.")
        message = generation.message
        try:
            func_call = copy.deepcopy(message.additional_kwargs["function_call"])
        except KeyError as exc:
            raise OutputParserException(
                f"Could not parse function call: {exc}",
                llm_output=msg_to_str(message),
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
            raise OutputParserException(
                f"Could not parse function call: {exc}",
                llm_output=msg_to_str(message),
            )
        return pydantic_args

    def _pre_parse_function_call(self, result: list[Generation]) -> dict:
        generation = result[0]
        if not isinstance(generation, ChatGeneration):
            raise OutputParserException("This output parser can only be used with a chat generation.")
        message = generation.message
        try:
            func_call = copy.deepcopy(message.additional_kwargs["function_call"])
        except KeyError:
            raise OutputParserException(
                "The model refused to respond with a " f"function call:\n{message.content}\n\n",
                llm_output=msg_to_str(message),
            )

        return func_call

    def _get_output_type(self, function_name: str) -> Type[M]:
        output_type_iter = filter(lambda t: t.__name__.lower() == function_name, self.output_types)
        if output_type_iter is None:
            raise OutputParserException(f"No parser found for function: {function_name}")
        return next(output_type_iter)
