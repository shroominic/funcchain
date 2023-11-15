from types import UnionType
from typing import TypeVar, Union

from langchain.chat_models.base import BaseChatModel
from langchain.output_parsers.openai_functions import PydanticOutputFunctionsParser
from langchain.prompts import ChatPromptTemplate
from langchain.schema import AIMessage, BaseMessage, BaseOutputParser, HumanMessage
from langchain.schema.chat_history import BaseChatMessageHistory
from langchain.schema.runnable import RunnableSequence, RunnableWithFallbacks
from PIL import Image
from pydantic.v1 import BaseModel

from ..settings import settings
from ..parser import MultiToolParser, ParserBaseModel
from ..utils import (
    from_docstring,
    get_output_type,
    is_function_model,
    is_vision_model,
    kwargs_from_parent,
    model_from_env,
    multi_pydantic_to_functions,
    parser_for,
    pydantic_to_functions,
)
from .prompt import create_prompt


ChainOutput = TypeVar("ChainOutput")


def create_union_chain(
    output_type: type[BaseModel],
    instruction: str,
    system: str,
    context: list[BaseMessage] = [],
    LLM: BaseChatModel | RunnableWithFallbacks | None = None,
    **input_kwargs: str,
) -> RunnableSequence[dict[str, str], ChainOutput]:
    output_types = output_type.__args__  # type: ignore
    output_type_names = [t.__name__ for t in output_types]

    input_kwargs[
        "format_instructions"
    ] = f"Extract to one of these output types: {output_type_names}."

    functions = multi_pydantic_to_functions(output_types)

    if isinstance(LLM, RunnableWithFallbacks):
        LLM = LLM.runnable.bind(**functions).with_fallbacks(
            [
                fallback.bind(**functions)
                for fallback in LLM.fallbacks
                if hasattr(LLM, "fallbacks")
            ]
        )
    else:
        LLM = LLM.bind(**functions)  # type: ignore

    prompt = create_prompt(
        system,
        instruction,
        context=[
            *context,
            HumanMessage(content="Can you use a function call for the next response?"),
            AIMessage(content="Yeah I can do that, just tell me what you need!"),
        ],
        images=[],
        **input_kwargs,
    )

    return prompt | LLM | MultiToolParser(output_types=output_types)  # type: ignore


def create_pydanctic_chain(
    output_type: type[BaseModel],
    prompt: ChatPromptTemplate,
    LLM: BaseChatModel | RunnableWithFallbacks,
    **input_kwargs: str,
) -> RunnableSequence[dict[str, str], ChainOutput]:
    input_kwargs["format_instructions"] = f"Extract to {output_type.__name__}."
    functions = pydantic_to_functions(output_type)
    LLM = (
        LLM.runnable.bind(**functions).with_fallbacks(  # type: ignore
            [
                fallback.bind(**functions)
                for fallback in LLM.fallbacks
                if hasattr(LLM, "fallbacks")
            ]
        )
        if isinstance(LLM, RunnableWithFallbacks)
        else LLM.bind(**functions)
    )
    return prompt | LLM | PydanticOutputFunctionsParser(pydantic_schema=output_type)  # type: ignore


def create_chain(
    system: str | None,
    instruction: str | None,
    parser: BaseOutputParser[ChainOutput] | None,
    context: list[BaseMessage],
    memory: BaseChatMessageHistory | None,
    input_kwargs: dict[str, str],
) -> RunnableSequence[dict[str, str], ChainOutput]:
    output_type = get_output_type()
    instruction = instruction or from_docstring()
    parser = parser or parser_for(output_type)
    input_kwargs.update(kwargs_from_parent())

    LLM = settings.LLM or model_from_env()
    func_model = is_function_model(LLM)

    if parser and not func_model:
        instruction = _add_format_instructions(parser, instruction, input_kwargs)

    images = [v for v in input_kwargs.values() if isinstance(v, Image.Image)]
    if is_vision_model(LLM):
        input_kwargs = {
            k: v for k, v in input_kwargs.items() if not isinstance(v, Image.Image)
        }
    elif images:
        raise RuntimeError("Images as input are only supported for vision models.")

    if memory:
        memory.add_user_message(instruction)
        context = memory.messages + context

    if not system:
        system = settings.DEFAULT_SYSTEM_PROMPT

    prompt = create_prompt(system, instruction, context, images=images, **input_kwargs)

    if func_model:
        if getattr(output_type, "__origin__", None) is Union or isinstance(
            output_type, UnionType
        ):
            return create_union_chain(
                output_type, instruction, system, context, LLM, **input_kwargs
            )

        if issubclass(output_type, BaseModel) and not issubclass(
            output_type, ParserBaseModel
        ):
            return create_pydanctic_chain(output_type, prompt, LLM, **input_kwargs)

    return prompt | LLM | parser  # type: ignore


def _add_format_instructions(
    parser: BaseOutputParser,
    instruction: str,
    input_kwargs: dict[str, str],
) -> str:
    try:
        if format_instructions := parser.get_format_instructions():
            instruction += "\n{format_instructions}"
            input_kwargs["format_instructions"] = format_instructions
        return instruction
    except NotImplementedError:
        return instruction
