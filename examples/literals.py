from typing import Literal

from funcchain import chain
from pydantic import BaseModel


# just a silly example to schowcase the Literal type
class Ranking(BaseModel):
    score: Literal[11, 22, 33, 44, 55]
    error: Literal["no_input", "all_good", "invalid"]


def rank_output(output: str) -> Ranking:
    """
    Analyze and rank the output.
    """
    return chain()


rank = rank_output("The quick brown fox jumps over the lazy dog.")

print(rank)
