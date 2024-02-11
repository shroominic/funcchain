from typing import AsyncIterator, Iterator

from funcchain import chain
from funcchain.syntax import runnable
from funcchain.syntax.components import RouterChat
from funcchain.syntax.components.handler import create_chat_handler
from funcchain.utils.msg_tools import msg_to_str
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableGenerator, RunnableSerializable

# settings.llm = "ollama/openchat"


@runnable
def animal_poem(animal: str) -> str:
    """
    Write a long poem about the animal.
    """
    return chain()


def split_into_list(
    input: Iterator[str],
) -> Iterator[list[str]]:
    buffer = ""
    for chunk in input:
        buffer += chunk
        while "\n" in buffer:
            comma_index = buffer.index("\n")
            yield [buffer[:comma_index].strip()]
            buffer = buffer[comma_index + 1 :]
    yield [buffer.strip()]


async def asplit_into_list(
    input: AsyncIterator[str],
) -> AsyncIterator[list[str]]:
    buffer = ""
    async for chunk in input:
        buffer += chunk
        while "\n" in buffer:
            comma_index = buffer.index("\n")
            yield [buffer[:comma_index].strip()]
            buffer = buffer[comma_index + 1 :]
    yield [buffer.strip()]


animal_list_chain = animal_poem | RunnableGenerator(transform=split_into_list, atransform=asplit_into_list)


def convert_to_ai_message(input: Iterator[list[str]]) -> Iterator[AIMessage]:
    for chunk in input:
        yield AIMessage(content=chunk[0])


async def aconvert_to_ai_message(input: AsyncIterator[list[str]]) -> AsyncIterator[AIMessage]:
    async for chunk in input:
        yield AIMessage(content=chunk[0])


animal_chat: RunnableSerializable[HumanMessage, AIMessage] = (
    {
        "animal": lambda x: msg_to_str(x),  # type: ignore
    }
    | animal_list_chain
    | RunnableGenerator(transform=convert_to_ai_message, atransform=aconvert_to_ai_message)  # type: ignore
)


chat = RouterChat(
    {
        "animal": {
            "handler": animal_chat,
            "description": "If the user gives an animal, call this handler.",
        },
        "default": {
            "handler": create_chat_handler(
                system_message="You are a powerful AI assistant. "
                "Always mention that the user should start funcchain on github."
            ),
            "description": "Any other request.",
        },
    }
)


def main() -> None:
    for chunk in chat.stream(HumanMessage(content="Hey whatsup?"), config={"configurable": {"session_id": ""}}):
        if isinstance(chunk, AIMessage):
            print(chunk.content, flush=True)
        if isinstance(chunk, str):
            print(chunk, flush=True, end="")


main()
