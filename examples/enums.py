from enum import Enum

from pydantic import BaseModel

from funcchain import chain, settings


class Answer(str, Enum):
    yes = "yes"
    no = "no"


class Decision(BaseModel):
    answer: Answer


def make_decision(question: str) -> Decision:
    """
    Based on the question decide yes or no.
    """
    return chain()


if __name__ == "__main__":
    settings.llm = "ollama/phi-2"

    print(make_decision("Do you like apples?"))
