import inspect
from typing import TypeVar

from langchain.chat_models import AzureChatOpenAI, ChatOpenAI
from langchain.output_parsers import BooleanOutputParser, PydanticOutputParser
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import (
    BaseMessage,
    BaseOutputParser,
    StrOutputParser,
    SystemMessage,
)
from langchain.schema.runnable import RunnableWithFallbacks
from langchain.callbacks import get_openai_callback
from pydantic import BaseModel

from funcchain import settings
from funcchain.parser import ParserBaseModel
from funcchain.utils import count_tokens, retry_parse, log

T = TypeVar("T")


def _get_llm() -> RunnableWithFallbacks:
    model_kwargs = {
        "temperature": settings.TEMPERATURE,
        "request_timeout": settings.REQUEST_TIMEOUT,
        "verbose": settings.VERBOSE,
        "openai_api_type": "azure",
        "openai_api_key": settings.AZURE_API_KEY,
        "openai_api_base": settings.AZURE_API_BASE,
        "openai_api_version": settings.AZURE_API_VERSION
    }
    short_llm = AzureChatOpenAI(
        model="gpt-4",
        deployment_name=settings.AZURE_DEPLOYMENT_NAME,
        **model_kwargs
    )
    long_llm = AzureChatOpenAI(
        model="gpt-4-32k",
        deployment_name=settings.AZURE_DEPLOYMENT_NAME_LONG,
        **model_kwargs
    )
    return short_llm.with_fallbacks([long_llm])


def _get_parent_frame(depth: int = 4) -> inspect.FrameInfo:
    return inspect.getouterframes(inspect.currentframe())[depth]


def _from_docstring() -> str:
    """
    Get the docstring of the parent caller function.
    """
    doc_str = (
        (caller_frame := _get_parent_frame())
        .frame.f_globals[caller_frame.function]
        .__doc__
    )
    return "\n".join([line.lstrip() for line in doc_str.split("\n")])


def _parser_from_type() -> BaseOutputParser:
    """
    Get the parser from the type annotation of the parent caller function.
    """
    output_type = (
        (caller_frame := _get_parent_frame())
        .frame.f_globals[caller_frame.function]
        .__annotations__["return"]
    )
    if output_type is str:
        return StrOutputParser()
    if output_type is bool:
        return BooleanOutputParser()
    if issubclass(output_type, ParserBaseModel):
        return output_type.output_parser()
    if issubclass(output_type, BaseModel):
        return PydanticOutputParser(pydantic_object=output_type)
    else:
        raise NotImplementedError(f"Unknown output type: {output_type}")


def _kwargs_from_parent() -> dict[str, str]:
    """
    Get the kwargs from the parent function.
    """
    return _get_parent_frame().frame.f_locals


def _create_prompt(
    instruction: str,
    system: str,
    context: list[BaseMessage] = [],
    **input_kwargs,
) -> ChatPromptTemplate:
    base_tokens = count_tokens(instruction + system)
    for k, v in input_kwargs.copy().items():
        if isinstance(v, str):
            content_tokens = count_tokens(v)
            if base_tokens + content_tokens > settings.MAX_TOKENS:
                input_kwargs[k] = v[: (settings.MAX_TOKENS - base_tokens) * 2 // 3]
                print("Truncated: ", len(input_kwargs[k]))

    return ChatPromptTemplate.from_messages(
        [SystemMessage(content=system)]
        + context
        + [
            HumanMessagePromptTemplate.from_template(template=instruction)
            if isinstance(instruction, str)
            else instruction
        ]
    )


@retry_parse(3)
def funcchain(
    instruction: str | None = None,
    system: str = settings.DEFAULT_SYSTEM_PROMPT,
    parser: BaseOutputParser[T] | None = None,
    context: list[BaseMessage] = [],
    /,
    **input_kwargs,
) -> T:  # type: ignore
    """
    Get response from chatgpt for provided instructions.
    """
    if instruction is None:
        instruction = _from_docstring()
    if parser is None:
        parser = _parser_from_type()
    input_kwargs.update(_kwargs_from_parent())
    chain_name = _get_parent_frame(3).function

    try:
        if format_instructions := parser.get_format_instructions():
            instruction += "\n\n" + "{format_instructions}"
            input_kwargs["format_instructions"] = format_instructions
    except NotImplementedError:
        pass

    prompt = _create_prompt(instruction, system, context, **input_kwargs)
    llm = _get_llm()

    with get_openai_callback() as cb:
        result = (prompt | llm | parser).invoke(input_kwargs)
        log(f"{cb.total_tokens:05}T / {cb.total_cost:.3f}$ - {chain_name}")
    return result


@retry_parse(3)
async def afuncchain(
    instruction: str | None = None,
    system: str = settings.DEFAULT_SYSTEM_PROMPT,
    parser: BaseOutputParser[T] | None = None,
    context: list[BaseMessage] = [],
    /,
    **input_kwargs,
) -> T:
    """
    Get response from chatgpt for provided instructions.
    """
    if instruction is None:
        instruction = _from_docstring()
    if parser is None:
        parser = _parser_from_type()
    input_kwargs.update(_kwargs_from_parent())
    chain_name = _get_parent_frame(3).function

    try:
        if format_instructions := parser.get_format_instructions():
            instruction += "\n\n" + "{format_instructions}"
            input_kwargs["format_instructions"] = format_instructions
    except NotImplementedError:
        pass

    prompt = _create_prompt(instruction, system, context, **input_kwargs)
    llm = _get_llm()

    with get_openai_callback() as cb:
        result = await (prompt | llm | parser).ainvoke(input_kwargs)
        log(f"{cb.total_tokens:05}T / {cb.total_cost:.3f}$ - {chain_name}")
    return result
