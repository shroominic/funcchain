from typing import TypeVar

from langchain.callbacks.base import Callbacks
from langchain.schema import BaseMessage, BaseOutputParser
from langchain.schema.chat_history import BaseChatMessageHistory

from ..settings import FuncchainSettings
from ..utils.decorators import get_parent_frame, log_openai_callback, retry_parse
from .creation import create_chain

T = TypeVar("T")


@retry_parse
@log_openai_callback
def invoke(
    system: str,
    instruction: str,
    parser: BaseOutputParser[T],
    context: list[BaseMessage],
    memory: BaseChatMessageHistory,
    settings: FuncchainSettings,
    input_kw: dict[str, str] = {},
    callbacks: Callbacks = None,
) -> T:  # type: ignore
    chain = create_chain(
        system,
        instruction,
        parser,
        context,
        memory,
        settings,
        input_kw,
    )
    result = chain.invoke(
        input_kw, {"run_name": get_parent_frame(5).function, "callbacks": callbacks}
    )

    if isinstance(result, str):
        # TODO: function calls?
        memory.add_ai_message(result)

    return result


@retry_parse
@log_openai_callback
async def ainvoke(
    system: str,
    instruction: str,
    parser: BaseOutputParser[T],
    context: list[BaseMessage],
    memory: BaseChatMessageHistory,
    settings: FuncchainSettings,
    input_kw: dict[str, str] = {},
    callbacks: Callbacks = None,
) -> T:
    chain = create_chain(
        system,
        instruction,
        parser,
        context,
        memory,
        settings,
        input_kw,
    )
    result = await chain.ainvoke(
        input_kw, {"run_name": get_parent_frame(5).function, "callbacks": callbacks}
    )

    if isinstance(result, str):
        # TODO: function calls?
        memory.add_ai_message(result)

    return result
