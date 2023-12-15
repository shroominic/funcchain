from PIL import Image
from pydantic import BaseModel, Field

from funcchain import chain, settings

settings.llm = "openai/gpt-4-vision-preview"
settings.streaming = True


class AnalysisResult(BaseModel):
    """The result of an image analysis."""

    theme: str = Field(description="The theme of the image")
    description: str = Field(description="A description of the image")
    objects: list[str] = Field(description="A list of objects found in the image")


def analyse_image(image: Image.Image) -> AnalysisResult:
    """
    Analyse the image and extract its
    theme, description and objects.
    """
    return chain()


if __name__ == "__main__":
    example_image = Image.open("examples/assets/old_chinese_temple.jpg")
    from funcchain.streaming import stream_to

    with stream_to(print):
        result = analyse_image(example_image)

    print("Theme:", result.theme)
    print("Description:", result.description)

    for obj in result.objects:
        print("Found this object:", obj)
