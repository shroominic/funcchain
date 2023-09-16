from typing import TypeVar

from langchain.pydantic_v1 import BaseModel
from langchain.callbacks import get_openai_callback
from langchain.schema import BaseMessage, BaseOutputParser
from langchain.output_parsers.openai_functions import PydanticOutputFunctionsParser
from langchain.chat_models import ChatOpenAI
from funcchain import settings
from funcchain.prompt import create_prompt
from funcchain.utils import (
    create_long_llm,
    from_docstring,
    gather_llm_type,
    get_parent_frame,
    get_output_type,
    kwargs_from_parent,
    pydantic_to_functions,
    log,
    parser_for,
    retry_parse,
)

T = TypeVar("T")


@retry_parse(3)
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
    output_type = get_output_type()
    chain_name = get_parent_frame(3).function
    if instruction is None:
        instruction = from_docstring()
    if parser is None:
        parser = parser_for(output_type)
    input_kwargs.update(kwargs_from_parent())

    try:
        if format_instructions := parser.get_format_instructions():
            instruction += "\n\n{format_instructions}"
            input_kwargs["format_instructions"] = format_instructions
    except NotImplementedError:
        pass

    prompt = create_prompt(instruction, system, context, **input_kwargs)
    llm = create_long_llm()

    match gather_llm_type(llm):
        case "base_model":
            raise NotImplementedError
        case "chat_model":
            result = (prompt | llm | parser).invoke(input_kwargs)
            log(f"N/A token - {chain_name}")
        case "openai_model":
            with get_openai_callback() as cb:
                result = (prompt | llm | parser).invoke(input_kwargs)
                log(f"{cb.total_tokens:05}T / {cb.total_cost:.3f}$ - {chain_name}")
        case "function_model":
            if issubclass(output_type, BaseModel):
                input_kwargs[
                    "format_instructions"
                ] = f"Extract to {output_type.__name__}."
                functions = pydantic_to_functions(output_type)
                llm = llm.runnable.bind(**functions).with_fallbacks(
                    [fallback.bind(**functions) for fallback in llm.fallbacks]
                )
                with get_openai_callback() as cb:
                    result = (
                        prompt
                        | llm
                        | PydanticOutputFunctionsParser(pydantic_schema=output_type)
                    ).invoke(input_kwargs)
                    log(
                        f"{cb.total_tokens:05}T / {cb.total_cost:.3f}$ - {chain_name} - function_call"
                    )
            else:
                with get_openai_callback() as cb:
                    result = (prompt | llm | parser).invoke(input_kwargs)
                    log(f"{cb.total_tokens:05}T / {cb.total_cost:.3f}$ - {chain_name}")
    return result


@retry_parse(3)
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
    output_type = get_output_type()
    chain_name = get_parent_frame(3).function
    if instruction is None:
        instruction = from_docstring()
    if parser is None:
        parser = parser_for(output_type)
    input_kwargs.update(kwargs_from_parent())

    try:
        if format_instructions := parser.get_format_instructions():
            instruction += "\n\n{format_instructions}"
            input_kwargs["format_instructions"] = format_instructions
    except NotImplementedError:
        pass

    prompt = create_prompt(instruction, system, context, **input_kwargs)
    llm = create_long_llm()

    match gather_llm_type(llm):
        case "base_model":
            raise NotImplementedError
        case "chat_model":
            result = await (prompt | llm | parser).ainvoke(input_kwargs)
            log(f"N/A token - {chain_name}")
        case "openai_model":
            with get_openai_callback() as cb:
                result = await (prompt | llm | parser).ainvoke(input_kwargs)
                log(f"{cb.total_tokens:05}T / {cb.total_cost:.3f}$ - {chain_name}")
        case "function_model":
            if issubclass(output_type, BaseModel):
                input_kwargs[
                    "format_instructions"
                ] = f"Extract to {output_type.__name__}."
                functions = pydantic_to_functions(output_type)
                llm = llm.runnable.bind(**functions).with_fallbacks(
                    [fallback.bind(**functions) for fallback in llm.fallbacks]
                )
                with get_openai_callback() as cb:
                    result = await (
                        prompt
                        | llm
                        | PydanticOutputFunctionsParser(pydantic_schema=output_type)
                    ).ainvoke(input_kwargs)
                    log(
                        f"{cb.total_tokens:05}T / {cb.total_cost:.3f}$ - {chain_name} - function_call"
                    )
            else:
                with get_openai_callback() as cb:
                    result = await (prompt | llm | parser).ainvoke(input_kwargs)
                    log(f"{cb.total_tokens:05}T / {cb.total_cost:.3f}$ - {chain_name}")
    return result
