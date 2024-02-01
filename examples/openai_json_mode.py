from funcchain import chain, settings
from pydantic import BaseModel

settings.console_stream = True


class FruitSalad(BaseModel):
    bananas: int = 0
    apples: int = 0


def sum_fruits(fruit_salad: FruitSalad) -> int:
    """
    Sum the number of fruits in a fruit salad.
    """
    return chain()


if __name__ == "__main__":
    fruit_salad = FruitSalad(bananas=3, apples=5)
    assert sum_fruits(fruit_salad) == 8
