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
from pydantic import BaseModel

from funcchain import settings
from funcchain.parser import ParserBaseModel
from funcchain.utils import count_tokens, retry

T = TypeVar("T")


def _get_llm() -> RunnableWithFallbacks:
    short_llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.01,
        request_timeout=60 * 5,
        verbose=settings.DEBUG,
        openai_api_key=settings.OPENAI_API_KEY,
    )
    long_llm = AzureChatOpenAI(
        temperature=0.01,
        model="gpt-4-32k",
        request_timeout=60 * 5,
        verbose=settings.DEBUG,
        openai_api_type="azure",
        deployment_name=settings.AZURE_DEPLOYMENT_NAME,
        openai_api_key=settings.AZURE_API_KEY,
        openai_api_base=settings.AZURE_API_BASE,
        openai_api_version=settings.AZURE_API_VERSION,
    )
    return short_llm.with_fallbacks([long_llm])


def _get_parent_frame() -> inspect.FrameInfo:
    return inspect.getouterframes(inspect.currentframe())[4]


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
    parser: BaseOutputParser,
    context: list[BaseMessage] = [],
    **input_kwargs,
) -> ChatPromptTemplate:
    base_tokens = count_tokens(instruction + system)
    for k, v in input_kwargs.copy().items():
        if isinstance(v, str):
            content_tokens = count_tokens(v)
            print("Tokens: ", content_tokens + base_tokens)
            if base_tokens + content_tokens > settings.MAX_TOKENS:
                tokens = settings.MAX_TOKENS - base_tokens
                input_kwargs[k] = v[: (tokens) * 2 // 3]
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


@retry(3)
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

    try:
        if format_instructions := parser.get_format_instructions():
            instruction += "\n\n" + "{format_instructions}"
            input_kwargs["format_instructions"] = format_instructions
    except NotImplementedError:
        pass

    return (
        _create_prompt(instruction, system, parser, context, **input_kwargs)
        | _get_llm()
        | parser
    ).invoke(input_kwargs)


@retry(3)
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

    try:
        if format_instructions := parser.get_format_instructions():
            instruction += "\n\n" + "{format_instructions}"
            input_kwargs["format_instructions"] = format_instructions
    except NotImplementedError:
        pass

    return await (
        _create_prompt(instruction, system, parser, context, **input_kwargs)
        | _get_llm()
        | parser
    ).ainvoke(input_kwargs)
