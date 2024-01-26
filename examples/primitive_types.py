from typing import Literal

from funcchain import chain, settings

settings.console_stream = True


def evaluate(sentence: str) -> tuple[Literal["good", "bad"], float, str]:
    """
    Evaluate the given sentence based on grammatical correctness and give it a score.
    """
    return chain()


result = evaluate("Hello, I am new to english language. Let's see how well I can write.")

print(type(result))
