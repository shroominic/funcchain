from typing import TypeVar
from langchain.schema.runnable import RunnableSequence
from langchain.schema.chat_history import BaseChatMessageHistory
from ..utils.decorators import retry_parse, log_openai_callback

T = TypeVar("T")


@retry_parse
@log_openai_callback
def invoke(
    chain: RunnableSequence[dict[str, str], T],
    memory: BaseChatMessageHistory | None,
    input: dict[str, str],
) -> T:  # type: ignore
    result = chain.invoke(input)

    if memory and isinstance(result, str):
        memory.add_ai_message(result)

    return result


@retry_parse
@log_openai_callback
async def ainvoke(
    chain: RunnableSequence[dict[str, str], T],
    memory: BaseChatMessageHistory | None,
    input: dict[str, str],
) -> T:
    result = await chain.ainvoke(input)

    if memory and isinstance(result, str):
        memory.add_ai_message(result)

    return result
