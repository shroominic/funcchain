from funcchain import chain
from pydantic import BaseModel


class FruitSalad(BaseModel):
    bananas: int = 0
    apples: int = 0


def sum_fruits(fruit_salad: FruitSalad) -> int:
    """
    Sum the number of fruits in a fruit salad.
    """
    return chain()


def test_fruit_salad() -> None:
    fruit_salad = FruitSalad(bananas=3, apples=5)
    assert sum_fruits(fruit_salad) == 8
