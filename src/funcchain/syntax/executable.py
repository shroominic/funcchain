from typing import TypeVar

from langchain.memory import ChatMessageHistory
from langchain_core.callbacks.base import Callbacks
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.runnables import Runnable

from ..backend.compiler import compile_chain
from ..backend.settings import SettingsOverride, create_local_settings
from ..schema.signature import Signature
from .meta_inspect import (
    from_docstring,
    get_output_type,
    get_parent_frame,
    kwargs_from_parent,
)

ChainOut = TypeVar("ChainOut")


def chain(
    system: str | None = None,
    instruction: str | None = None,
    context: list[BaseMessage] = [],
    memory: BaseChatMessageHistory | None = None,
    settings_override: SettingsOverride = {},
    **input_kwargs: str,
) -> ChainOut:  # type: ignore
    """
    Generate response of llm for provided instructions.
    """
    settings = create_local_settings(settings_override)
    callbacks: Callbacks = None
    output_type = get_output_type()

    memory = memory or ChatMessageHistory()
    input_kwargs.update(kwargs_from_parent())
    system = system or settings.default_system_prompt
    instruction = instruction or from_docstring()

    sig: Signature = Signature(
        instruction=instruction,
        input_args=list(input_kwargs.keys()),
        output_type=output_type,
        llm=settings_override.get("llm", settings.llm),
        history=context,
        settings=settings,
    )
    chain: Runnable[dict[str, str], ChainOut] = compile_chain(sig)
    result = chain.invoke(input_kwargs, {"run_name": get_parent_frame(3).function, "callbacks": callbacks})

    if memory and isinstance(result, str):
        # TODO: function calls?
        memory.add_ai_message(result)

    return result


async def achain(
    system: str | None = None,
    instruction: str | None = None,
    context: list[BaseMessage] = [],
    memory: BaseChatMessageHistory | None = None,
    settings_override: SettingsOverride = {},
    **input_kwargs: str,
) -> ChainOut:
    """
    Asyncronously generate response of llm for provided instructions.
    """
    settings = create_local_settings(settings_override)
    callbacks: Callbacks = None
    output_type = get_output_type()

    memory = memory or ChatMessageHistory()
    input_kwargs.update(kwargs_from_parent())
    system = system or settings.default_system_prompt
    instruction = instruction or from_docstring()

    sig: Signature = Signature(
        instruction=instruction,
        input_args=list(input_kwargs.keys()),
        output_type=output_type,
        llm=settings_override.get("llm", settings.llm),
        history=context,
        settings=settings,
    )
    chain: Runnable[dict[str, str], ChainOut] = compile_chain(sig)
    result = await chain.ainvoke(input_kwargs, {"run_name": get_parent_frame(5).function, "callbacks": callbacks})

    if memory and isinstance(result, str):
        # TODO: function calls?
        memory.add_ai_message(result)

    return result


def runnable(
    instruction: str,
    output_type: type[ChainOut],
    input_args: list[str] = [],
    context: list = [],
    llm: BaseChatModel | str | None = None,
    system: str = "",
    settings_override: SettingsOverride = {},
) -> Runnable[dict[str, str], ChainOut]:
    """
    Experimental replacement for using the funcchain syntax.
    """
    if settings_override and llm:
        settings_override["llm"] = llm
    instruction = "\n" + instruction
    settings = create_local_settings(settings_override)
    context = [SystemMessage(content=system)] + context

    sig: Signature = Signature(
        instruction=instruction,
        input_args=input_args,
        output_type=output_type,
        llm=settings_override.get("llm", settings.llm),
        history=context,
        settings=settings,
    )

    return compile_chain(sig)
