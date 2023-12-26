from typing import TypeVar, Type
from langchain_core.runnables import RunnableSerializable
from langchain.memory import ChatMessageHistory
from .creation import create_chain
from ..settings import SettingsOverride, get_settings

T = TypeVar("T")


def runnable(
    instruction: str,
    output_type: Type[T],
    input_args: list[str] = [],
    context: list = [],
    system: str = "",
    settings_override: SettingsOverride | None = None,
) -> RunnableSerializable[dict[str, str], T]:
    """
    Experimental replacement for using the funcchain syntax.
    """
    instruction = "\n" + instruction
    chain: RunnableSerializable[dict[str, str], T] = create_chain(
        system=system,
        instruction=instruction,
        output_type=output_type,
        context=context,
        memory=ChatMessageHistory(),
        settings=get_settings(settings_override),
        input_kwargs={k: "" for k in input_args},
    )

    # TODO: rewrite without original chain creation
    # gather llm
    # evaluate model capabilities
    # get
    # create prompt template

    return chain
