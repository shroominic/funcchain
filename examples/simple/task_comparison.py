import asyncio

from funcchain import achain, chain
from pydantic import BaseModel


class Task(BaseModel):
    name: str
    description: str
    difficulty: str
    keywords: list[str]

    def __str__(self) -> str:
        return self.model_dump_json(indent=2)


def description(task: Task) -> str:
    """
    CREATE TASK DESCRIPTION: {task}
    """
    return chain()


def extract_task(task_description: str) -> Task:
    """
    EXTRACT TASK: {task_description}
    """
    return chain()


async def compare_tasks(task1: Task, task2: Task) -> bool:
    """
    COMPARE TASKS:
    1: {task1}
    2: {task2}

    Are the tasks kind of equal?
    """
    return await achain()


def test_extraction() -> None:
    task = Task(
        name="Do dishes",
        description="Do the dishes in the kitchen.",
        difficulty="easy",
        keywords=["kitchen", "dishes"],
    )

    task_description = description(task)

    extracted_task = extract_task(task_description)

    assert asyncio.run(compare_tasks(task, extracted_task))


if __name__ == "__main__":
    test_extraction()
