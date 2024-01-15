from typing import TypedDict

from langchain_core.chat_history import BaseChatMessageHistory


class ImageURL(TypedDict):
    """Funcchain type for passing an image as external url."""

    url: str


class ChatHistory(BaseChatMessageHistory):
    """Funcchain Type Wrapper for detecting ChatHistorys."""

    ...
