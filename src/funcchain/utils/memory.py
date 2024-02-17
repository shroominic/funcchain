from typing import Any

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.pydantic_v1 import BaseModel, Field

from ..schema.types import ChatHistoryFactory


class ChatMessageHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history.

    Stores messages in an in memory list.

    This is a copy from `langchain_community.chat_message_histories.in_memory.ChatMessageHistory`
    to not require langchain_community as dependency only for this feature.
    """

    messages: list[BaseMessage] = Field(default_factory=list)

    def add_message(self, message: BaseMessage) -> None:
        """Add a self-created message to the store"""
        self.messages.append(message)

    def clear(self) -> None:
        self.messages = []


_in_memory_database: dict[str, list[BaseMessage]] = {}


class InMemoryChatMessageHistory(BaseChatMessageHistory):
    """In memory implementation of chat message history.

    Stores messages in an in memory list.
    """

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        if session_id not in _in_memory_database:
            _in_memory_database[session_id] = []

    @property
    def messages(self) -> list[BaseMessage]:  # type: ignore
        return _in_memory_database[self.session_id]

    def add_message(self, message: BaseMessage) -> None:
        _in_memory_database[self.session_id].append(message)

    def add_messages(self, messages: list[BaseMessage]) -> None:  # type: ignore
        _in_memory_database[self.session_id].extend(messages)

    def clear(self) -> None:
        print(f"Clearing {self.session_id}")
        del _in_memory_database[self.session_id][:]


def create_history_factory(
    backend: type[BaseChatMessageHistory],
    backend_kwargs: dict[str, Any] = {},
) -> ChatHistoryFactory:
    """
    Create a function that returns a chat history.
    """

    def history_factory(session_id: str, **kwargs: Any) -> BaseChatMessageHistory:
        kwargs["session_id"] = session_id
        kwargs.update(backend_kwargs)
        return backend(**kwargs)

    return history_factory
