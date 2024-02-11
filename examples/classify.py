from typing import Literal

from funcchain import chain


def classify(
    text: str,
) -> Literal["happy", "sad", "flirty"]:
    """
    Classify the text as happy, sad, flirty, or neural.
    """
    return chain()


if __name__ == "__main__":
    r = classify("Hey :)")
    print(r)
    assert r == "happy"

    r = classify("Hey :(")
    print(r)
    assert r == "sad"

    r = classify("Hey ;)")
    print(r)
    assert r == "flirty"
