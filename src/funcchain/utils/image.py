from __future__ import annotations

from base64 import b64decode, b64encode
from io import BytesIO
from typing import TYPE_CHECKING

from ..syntax.input_types import Image

if TYPE_CHECKING:
    from PIL.Image import Image as PImage
    from PIL.Image import open as pil_open
else:
    PImage = type("PImage")
    pil_open = lambda x: x  # noqa


def image_to_base64_url(image: Image) -> str:
    return image.url


def base64_url_to_image(base64_url: str) -> Image:
    return Image(base64_url)


def pillow_image_to_base64_url(image: PImage) -> str:
    with BytesIO() as output:
        image.save(output, format="PNG")
        base64_image = b64encode(output.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{base64_image}"


def base64_url_to_pillow_image(base64_url: str) -> PImage:
    base64_image = base64_url.split(",")[1]
    image_bytes = b64decode(base64_image)
    image = pil_open(BytesIO(image_bytes))
    return image
