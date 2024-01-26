from typing import Any, TypeVar

from langchain_core.callbacks.base import Callbacks
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.runnables import Runnable

from ..backend.compiler import compile_chain
from ..backend.meta_inspect import (
    args_from_parent,
    from_docstring,
    get_output_types,
    get_parent_frame,
    kwargs_from_parent,
)
from ..backend.settings import SettingsOverride, create_local_settings
from ..schema.signature import Signature
from ..utils.memory import ChatMessageHistory
from .input_types import Image


def chain(
    *,
    system: str | None = None,
    instruction: str | None = None,
    context: list[BaseMessage] = [],
    memory: BaseChatMessageHistory | None = None,
    settings_override: SettingsOverride = {},
    **input_kwargs: Any,
) -> Any:
    """
    Generate response of llm for provided instructions.
    """
    settings = create_local_settings(settings_override)
    callbacks: Callbacks = None
    output_types = get_output_types()
    input_args: list[tuple[str, type]] = args_from_parent()

    memory = memory or ChatMessageHistory()
    input_kwargs.update(kwargs_from_parent())

    # todo maybe this should be done in the prompt processor?
    system = system or settings.system_prompt
    instruction = instruction or from_docstring()

    # temp image handling
    temp_images: list[Image] = []
    for k, v in input_kwargs.copy().items():
        if isinstance(v, Image):
            temp_images.append(v)
            input_kwargs.pop(k)

    sig: Signature = Signature(
        instruction=instruction,
        input_args=input_args,
        output_types=output_types,
        history=context,
        settings=settings,
    )
    chain: Runnable[dict[str, Any], Any] = compile_chain(sig, temp_images)
    result = chain.invoke(input_kwargs, {"run_name": get_parent_frame(3).function, "callbacks": callbacks})

    if memory and isinstance(result, str):
        # TODO: function calls?
        memory.add_ai_message(result)

    return result


async def achain(
    *,
    system: str | None = None,
    instruction: str | None = None,
    context: list[BaseMessage] = [],
    memory: BaseChatMessageHistory | None = None,
    settings_override: SettingsOverride = {},
    **input_kwargs: Any,
) -> Any:
    """
    Asyncronously generate response of llm for provided instructions.
    """
    settings = create_local_settings(settings_override)
    callbacks: Callbacks = None
    output_types = get_output_types()
    input_args: list[tuple[str, type]] = args_from_parent()

    memory = memory or ChatMessageHistory()
    input_kwargs.update(kwargs_from_parent())

    # todo maybe this should be done in the prompt processor?
    system = system or settings.system_prompt
    instruction = instruction or from_docstring()

    # temp image handling
    temp_images: list[Image] = []
    for v, k in input_kwargs.copy().items():
        if isinstance(v, Image):
            temp_images.append(v)
            input_kwargs.pop(k)

    sig: Signature = Signature(
        instruction=instruction,
        input_args=input_args,
        output_types=output_types,
        history=context,
        settings=settings,
    )
    chain: Runnable[dict[str, str], Any] = compile_chain(sig, temp_images)
    result = await chain.ainvoke(input_kwargs, {"run_name": get_parent_frame(5).function, "callbacks": callbacks})

    if memory and isinstance(result, str):
        # TODO: function calls?
        memory.add_ai_message(result)

    return result


ChainOut = TypeVar("ChainOut")


def compile_runnable(
    *,
    instruction: str,
    output_types: list[type[ChainOut]],
    input_args: list[str] = [],
    context: list = [],
    llm: BaseChatModel | str | None = None,
    system: str = "",
    settings_override: SettingsOverride = {},
) -> Runnable[dict[str, str], ChainOut]:
    """
    On the fly compilation of the funcchain syntax.
    """
    if settings_override and llm:
        settings_override["llm"] = llm
    instruction = "\n" + instruction
    settings = create_local_settings(settings_override)
    context = [SystemMessage(content=system)] + context
    _input_args: list[tuple[str, type]] = [(arg, str) for arg in input_args]

    sig: Signature = Signature(
        instruction=instruction,
        input_args=_input_args,
        output_types=output_types,
        history=context,
        settings=settings,
    )

    return compile_chain(sig, temp_images=[])
