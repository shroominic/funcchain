from typing import Any, TypeVar, Union

from langchain.callbacks import get_openai_callback
from langchain.output_parsers.openai_functions import PydanticOutputFunctionsParser
from langchain.pydantic_v1 import BaseModel
from langchain.schema import AIMessage, BaseMessage, BaseOutputParser, HumanMessage
from langchain.schema.runnable import RunnableSequence, RunnableWithFallbacks

from funcchain.config import settings
from funcchain.parser import MultiToolParser, ParserBaseModel
from funcchain.prompt import create_prompt
from funcchain.utils import (
    from_docstring,
    get_output_type,
    get_parent_frame,
    is_function_model,
    kwargs_from_parent,
    log,
    model_from_env,
    multi_pydantic_to_functions,
    parser_for,
    pydantic_to_functions,
    retry_parse,
)

T = TypeVar("T")


def create_chain(
    instruction: str | None = None,
    system: str = settings.DEFAULT_SYSTEM_PROMPT,
    parser: BaseOutputParser[T] | None = None,
    context: list[BaseMessage] = [],
    input_kwargs: dict[str, Any] = {},
) -> RunnableSequence:
    output_type = get_output_type()
    instruction = instruction or from_docstring()
    parser = parser or parser_for(output_type)
    input_kwargs.update(kwargs_from_parent())

    _add_format_instructions(parser, instruction, input_kwargs)

    prompt = create_prompt(instruction, system, context, **input_kwargs)
    LLM = settings.LLM or model_from_env()

    if is_function_model(LLM):
        if getattr(output_type, "__origin__", None) is Union:
            output_types = output_type.__args__  # type: ignore
            output_type_names = [t.__name__ for t in output_types]

            input_kwargs["format_instructions"] = f"Extract to one of these output types: {output_type_names}."

            functions = multi_pydantic_to_functions(output_types)

            if isinstance(LLM, RunnableWithFallbacks):
                LLM = LLM.runnable.bind(**functions).with_fallbacks(
                    [fallback.bind(**functions) for fallback in LLM.fallbacks if hasattr(LLM, "fallbacks")]
                )
            else:
                LLM = LLM.bind(**functions)  # type: ignore

            prompt = create_prompt(
                instruction,
                system,
                [
                    HumanMessage(content="Can you use a function call for the next response?"),
                    AIMessage(content="Yeah I can do that, just tell me what you need!"),
                ],
                **input_kwargs,
            )

            return prompt | LLM | MultiToolParser(output_types=output_types)
        if issubclass(output_type, BaseModel) and not issubclass(output_type, ParserBaseModel):
            input_kwargs["format_instructions"] = f"Extract to {output_type.__name__}."
            functions = pydantic_to_functions(output_type)
            if isinstance(LLM, RunnableWithFallbacks):
                LLM = LLM.runnable.bind(**functions).with_fallbacks(
                    [fallback.bind(**functions) for fallback in LLM.fallbacks if hasattr(LLM, "fallbacks")]
                )
            else:
                LLM = LLM.bind(**functions)  # type: ignore
            return prompt | LLM | PydanticOutputFunctionsParser(pydantic_schema=output_type)
    return prompt | LLM | parser


def _add_format_instructions(
    parser: BaseOutputParser,
    instruction: str,
    input_kwargs: dict,
) -> None:
    try:
        if format_instructions := parser.get_format_instructions():
            instruction += "\n\n{format_instructions}"
            input_kwargs["format_instructions"] = format_instructions
    except NotImplementedError:
        pass


@retry_parse(5)
def chain(
    instruction: str | None = None,
    system: str = settings.DEFAULT_SYSTEM_PROMPT,
    parser: BaseOutputParser[T] | None = None,
    context: list[BaseMessage] = [],
    **input_kwargs,
) -> T:  # type: ignore
    """
    Get response from chatgpt for provided instructions.
    """
    with get_openai_callback() as cb:
        chain = create_chain(instruction, system, parser, context, input_kwargs).invoke(input_kwargs)
        if cb.total_tokens != 0:
            log(f"{cb.total_tokens:05}T / {cb.total_cost:.3f}$ - {get_parent_frame(3).function}")
    return chain


@retry_parse(5)
async def achain(
    instruction: str | None = None,
    system: str = settings.DEFAULT_SYSTEM_PROMPT,
    parser: BaseOutputParser[T] | None = None,
    context: list[BaseMessage] = [],
    **input_kwargs,
) -> T:
    """
    Get response from chatgpt for provided instructions.
    """
    with get_openai_callback() as cb:
        chain = await create_chain(instruction, system, parser, context, input_kwargs).ainvoke(input_kwargs)
        if cb.total_tokens != 0:
            log(f"{cb.total_tokens:05}T / {cb.total_cost:.3f}$ - {get_parent_frame(3).function}")
    return chain
