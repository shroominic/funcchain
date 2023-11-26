from typing import TypeVar

from langchain.memory import ChatMessageHistory
from langchain.schema import BaseMessage, BaseOutputParser
from langchain.schema.chat_history import BaseChatMessageHistory

from .invoke import invoke, ainvoke


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
    return invoke(
        system,
        instruction,
        parser,
        context,
        memory or ChatMessageHistory(),
        input_kwargs,
    )


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
    return await ainvoke(
        system,
        instruction,
        parser,
        context,
        memory or ChatMessageHistory(),
        input_kwargs,
    )
