from typing import TypeVar

from langchain.schema import BaseMessage, BaseOutputParser
from langchain.schema.chat_history import BaseChatMessageHistory

from .invoke import invoke, ainvoke
from .creation import create_chain


ChainOutput = TypeVar("ChainOutput")


def chain(
    system: str | None = None,
    instruction: str | None = None,
    context: list[BaseMessage] = [],
    memory: BaseChatMessageHistory | None = None,
    parser: BaseOutputParser[ChainOutput] | None = None,
    **input_kwargs: str,
) -> ChainOutput:  # type: ignore
    """
    Generate response of llm for provided instructions.
    """
    chain = create_chain(system, instruction, parser, context, memory, input_kwargs)
    return invoke(chain, memory, input_kwargs)


async def achain(
    system: str | None = None,
    instruction: str | None = None,
    context: list[BaseMessage] = [],
    memory: BaseChatMessageHistory | None = None,
    parser: BaseOutputParser[ChainOutput] | None = None,
    **input_kwargs: str,
) -> ChainOutput:
    """
    Asyncronously generate response of llm for provided instructions.
    """
    chain = create_chain(system, instruction, parser, context, memory, input_kwargs)
    return await ainvoke(chain, memory, input_kwargs)
