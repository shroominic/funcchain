from typing import Union

from langchain_core.messages import BaseMessage as _BaseMessage
from langchain_core.messages import BaseMessageChunk

BaseMessage = Union[_BaseMessage, BaseMessageChunk]


def msg_images(msg: BaseMessage) -> list[str]:
    """Return a list of image URLs in the message content."""
    if isinstance(msg.content, str):
        return []
    return [item["image_url"]["url"] for item in msg.content if isinstance(item, dict) and item["type"] == "image_url"]


def msg_to_str(msg: BaseMessage) -> str:
    """Return the message content."""
    return (
        msg.content
        if isinstance(msg.content, str)
        else msg.content[0]
        if isinstance(msg.content[0], str)
        else msg.content[0]["text"]
    )
