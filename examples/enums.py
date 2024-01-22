from enum import Enum

from funcchain import chain
from pydantic import BaseModel


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
    print(make_decision("Do you like apples?"))
