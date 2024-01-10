from base64 import b64decode, b64encode
from io import BytesIO

from PIL import Image


def image_to_base64_url(image: Image.Image) -> str:
    with BytesIO() as output:
        image.save(output, format="PNG")
        base64_image = b64encode(output.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{base64_image}"


def base64_url_to_image(base64_url: str) -> Image.Image:
    base64_image = base64_url.split(",")[1]
    image_bytes = b64decode(base64_image)
    image = Image.open(BytesIO(image_bytes))
    return image
