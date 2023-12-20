from typing import TypeVar

from langchain.memory import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage

from ..settings import SettingsOverride, get_settings
from .invoke import ainvoke, invoke

ChainOutput = TypeVar("ChainOutput")


def chain(
    system: str | None = None,
    instruction: str | None = None,
    context: list[BaseMessage] = [],
    memory: BaseChatMessageHistory | None = None,
    settings_override: SettingsOverride | None = None,
    **input_kwargs: str,
) -> ChainOutput:  # type: ignore
    """
    Generate response of llm for provided instructions.
    """
    return invoke(
        system,
        instruction,
        context,
        memory or ChatMessageHistory(),
        get_settings(settings_override),
        input_kwargs,
    )


async def achain(
    system: str | None = None,
    instruction: str | None = None,
    context: list[BaseMessage] = [],
    memory: BaseChatMessageHistory | None = None,
    settings_override: SettingsOverride | None = None,
    **input_kwargs: str,
) -> ChainOutput:
    """
    Asyncronously generate response of llm for provided instructions.
    """
    return await ainvoke(
        system,
        instruction,
        context,
        memory or ChatMessageHistory(),
        get_settings(settings_override),
        input_kwargs,
    )
