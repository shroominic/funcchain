from typing import TypeVar
from langchain.schema.runnable import RunnableSequence
from langchain.schema.chat_history import BaseChatMessageHistory
from langchain.callbacks.base import Callbacks
from ..utils.decorators import retry_parse, log_openai_callback, get_parent_frame

T = TypeVar("T")


@retry_parse
@log_openai_callback
def invoke(
    chain: RunnableSequence[dict[str, str], T],
    memory: BaseChatMessageHistory | None,
    input: dict[str, str],
    callbacks: Callbacks = None,
) -> T:  # type: ignore
    result = chain.invoke(
        input, {"run_name": get_parent_frame(5).function, "callbacks": callbacks}
    )

    if memory and isinstance(result, str):
        memory.add_ai_message(result)

    return result


@retry_parse
@log_openai_callback
async def ainvoke(
    chain: RunnableSequence[dict[str, str], T],
    memory: BaseChatMessageHistory | None,
    input: dict[str, str],
    callbacks: Callbacks = None,
) -> T:
    result = await chain.ainvoke(
        input, {"run_name": get_parent_frame(5).function, "callbacks": callbacks}
    )

    if memory and isinstance(result, str):
        memory.add_ai_message(result)

    return result
