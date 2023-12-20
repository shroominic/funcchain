from typing import TypeVar, Any

from langchain_core.callbacks.base import Callbacks
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableSerializable

from ..settings import FuncchainSettings
from .creation import create_chain
from ..utils import (
    from_docstring,
    get_output_type,
    kwargs_from_parent,
    get_parent_frame,
    log_openai_callback,
    retry_parse,
)

T = TypeVar("T")


@retry_parse
@log_openai_callback
def invoke(
    system: str | None,
    instruction: str | None,
    context: list[BaseMessage],
    memory: BaseChatMessageHistory,
    settings: FuncchainSettings,
    input_kw: dict[str, str] = {},
    callbacks: Callbacks = None,
) -> Any:  # type: ignore
    # default values
    output_type = get_output_type()
    input_kw.update(kwargs_from_parent())
    system = system or settings.default_system_prompt
    instruction = instruction or from_docstring()

    chain: RunnableSerializable[dict[str, str], Any] = create_chain(
        system,
        instruction,
        output_type,
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
    system: str | None,
    instruction: str | None,
    context: list[BaseMessage],
    memory: BaseChatMessageHistory,
    settings: FuncchainSettings,
    input_kw: dict[str, str] = {},
    callbacks: Callbacks = None,
) -> Any:
    # default values
    output_type = get_output_type()
    input_kw.update(kwargs_from_parent())
    system = system or settings.default_system_prompt
    instruction = instruction or from_docstring()

    chain: RunnableSerializable[dict[str, str], Any] = create_chain(
        system,
        instruction,
        output_type,
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
