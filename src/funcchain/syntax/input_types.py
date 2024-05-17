import base64
from typing import TYPE_CHECKING

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage

from ..utils.msg_tools import msg_images

if TYPE_CHECKING:
    from PIL.Image import Image as PImage
    from PIL.Image import open as pil_open
else:
    PImage = type("PImage")
    pil_open = lambda x: x  # noqa


class Image:
    """
    Funcchain type for passing an image.
    Supports multiple input and output formats.
    (base64, bytes, pillow, file, web_url)
    """

    __slots__ = ("url",)

    def __init__(self, base64_url: str) -> None:
        self.url = base64_url

    def from_bytes(self, data: bytes) -> "Image":
        encoded_string = base64.b64encode(data).decode()
        return self.from_base64(encoded_string)

    @classmethod
    def from_message(cls, message: BaseMessage) -> list["Image"]:
        return [cls(i) for i in images] if (images := msg_images(message)) else []

    @classmethod
    def from_base64(cls, base64: str) -> "Image":
        return cls("data:image/png;base64," + base64)

    @classmethod
    def from_file(cls, path: str) -> "Image":
        with open(path, "rb") as file:
            encoded_string = base64.b64encode(file.read()).decode()
        return cls("data:image/png;base64," + encoded_string)

    @classmethod
    def from_pillow(cls, image: PImage) -> "Image":
        encoded_string = base64.b64encode(image.tobytes()).decode()
        return cls("data:image/png;base64," + encoded_string)

    @classmethod
    def from_url(cls, url: str) -> "Image":
        from requests import get  # type: ignore

        response_content = get(url).content
        encoded_string = base64.b64encode(response_content).decode()
        return cls("data:image/png;base64," + encoded_string)

    def to_base64(self) -> str:
        return self.url.split(",")[1]

    def to_bytes(self) -> bytes:
        base64_str = self.to_base64()
        return base64.b64decode(base64_str)

    def to_pillow(self) -> PImage:
        from io import BytesIO

        image_bytes = self.to_bytes()
        return pil_open(BytesIO(image_bytes))

    def to_file(self, path: str) -> None:
        open(path, "wb").write(self.to_bytes())

    def __str__(self) -> str:
        return self.url


# TODO: implement
class ChatHistory(BaseChatMessageHistory):
    """Funcchain Type Wrapper for detecting ChatHistorys."""

    ...
