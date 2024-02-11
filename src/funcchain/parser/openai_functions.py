import copy
from typing import Generic, Type, TypeVar

from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import BaseGenerationOutputParser
from langchain_core.outputs import ChatGeneration, Generation
from langchain_core.runnables import Runnable
from pydantic import BaseModel, ValidationError

from ..schema.types import UniversalChatModel
from ..syntax.output_types import CodeBlock as CodeBlock
from ..utils.msg_tools import msg_to_str

M = TypeVar("M", bound=BaseModel)


class RetryOpenAIFunctionPydanticParser(BaseGenerationOutputParser[M]):
    pydantic_schema: Type[M]
    args_only: bool = False
    retry: int
    retry_llm: UniversalChatModel = None

    def parse_result(self, result: list[Generation], *, partial: bool = False) -> M:
        try:
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
                pydantic_args = self.pydantic_schema.model_validate_json(func_call)
            else:
                pydantic_args = self.pydantic_schema.model_validate_json(func_call["arguments"])

            return pydantic_args
        except ValidationError as e:
            if self.retry > 0:
                print(f"Retrying parsing {self.pydantic_schema.__name__}...")
                return self.retry_chain.invoke(
                    input={"output": result, "error": str(e)},
                    config={"run_name": "RetryOpenAIFunctionPydanticParser"},
                )
            # no retries left
            raise OutputParserException(str(e), llm_output=msg_to_str(message))

    @property
    def retry_chain(self) -> Runnable:
        from ..syntax.executable import compile_runnable

        return compile_runnable(
            instruction="Retry parsing the output by fixing the error.",
            input_args=["output", "error"],
            output_types=[self.pydantic_schema],
            llm=self.retry_llm,
            settings_override={"retry_parse": self.retry - 1},
        )


class RetryOpenAIFunctionPydanticUnionParser(BaseGenerationOutputParser[M]):
    output_types: list[type[M]]
    args_only: bool = False
    retry: int
    retry_llm: UniversalChatModel = None

    def parse_result(self, result: list[Generation], *, partial: bool = False) -> M:
        try:
            function_call = self._pre_parse_function_call(result)

            output_type_names = [t.__name__.lower() for t in self.output_types]

            if function_call["name"] not in output_type_names:
                raise OutputParserException("Invalid function call")

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
                pydantic_args = output_type.model_validate_json(func_call["arguments"])
            else:
                pydantic_args = output_type.model_validate_json(func_call["arguments"])

            return pydantic_args
        except (ValidationError, OutputParserException) as e:
            if self.retry > 0:
                print(f"Retrying parsing {output_type.__name__}...")
                return self.retry_chain.invoke(
                    input={"output": result, "error": str(e)},
                    config={"run_name": "RetryOpenAIFunctionPydanticUnionParser"},
                )
            # no retries left
            raise OutputParserException(str(e), llm_output=msg_to_str(message))

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

    @property
    def retry_chain(self) -> Runnable:
        from ..syntax.executable import compile_runnable

        return compile_runnable(
            instruction="Retry parsing the output by fixing the error.",
            input_args=["output", "error"],
            output_types=self.output_types,
            llm=self.retry_llm,
            settings_override={"retry_parse": self.retry - 1},
        )


class RetryOpenAIFunctionPrimitiveTypeParser(RetryOpenAIFunctionPydanticParser, Generic[M]):
    """
    Parse primitve types by wrapping them in a PydanticModel and parsing them.
    Examples: int, float, bool, list[str], dict[str, int], Literal["a", "b", "c"], etc.
    """

    def parse_result(self, result: list[Generation], *, partial: bool = False) -> M:
        return super().parse_result(result, partial=partial).value
