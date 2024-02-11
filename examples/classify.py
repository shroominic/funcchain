from typing import Literal

from funcchain import chain


def classify(
    text: str,
) -> Literal["energetic", "sad", "flirty", "neural"]:
    """
    Classify the text.
    """
    return chain()


print(
    classify("Hello my name is Jeff."),
)
