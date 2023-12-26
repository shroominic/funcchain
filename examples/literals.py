from typing import Literal
from funcchain import chain
from pydantic import BaseModel


class Ranking(BaseModel):
    chain_of_thought: str
    score: Literal[11, 22, 33, 44, 55]


def rank_output(output: str) -> Ranking:
    """
    Analyze and rank the output.
    """
    return chain()


rank = rank_output("The quick brown fox jumps over the lazy dog.")

print(rank)
