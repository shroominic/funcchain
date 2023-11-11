from base64 import b64encode
from io import BytesIO

from PIL import Image


def image_to_base64_url(image: Image.Image) -> str:
    with BytesIO() as output:
        image.save(output, format="PNG")
        base64_image = b64encode(output.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{base64_image}"
