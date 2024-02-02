from asyncio import gather
from asyncio import run as _await
from random import shuffle

from funcchain import achain, settings
from pydantic import BaseModel

settings.temperature = 1


async def generate_answer(question: str) -> str:
    """
    {question}
    """
    return await achain()


class RankedAnswer(BaseModel):
    selected_answer: int


async def rank_answers(question: str, answers: list[tuple[int, str]]) -> RankedAnswer:
    """
    Given the list of answers, select the answer that answers the question best and is most accurate.
    """
    return await achain()


async def expert_answer(question: str) -> str:
    answers = await gather(*(generate_answer(question) for _ in range(15)))
    # Shuffle the answers to ensure randomness
    enum_answers = list(enumerate(answers))
    shuffle(enum_answers)
    ranked_answers = await gather(*(rank_answers(question, enum_answers) for _ in range(3)))
    highest_ranked_answer = max(
        ranked_answers,
        key=lambda x: sum(1 for ans in ranked_answers if ans.selected_answer == x.selected_answer),
    ).selected_answer
    return answers[highest_ranked_answer]


if __name__ == "__main__":
    question = "What is the best way to make coffee with only hot water and beans?"

    answer = _await(expert_answer(question))

    print(answer)

    assert isinstance(answer, str)
