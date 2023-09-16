from langchain.pydantic_v1 import BaseModel

from funcchain import chain


class Task(BaseModel):
    name: str
    description: str
    difficulty: str
    keywords: list[str]

    def __str__(self) -> str:
        return self.json(indent=2)


def description(task: Task) -> str:
    """
    CREATE TASK DESCRIPTION: {task}
    """
    return chain()


def extract_task(task: Task) -> Task:
    """
    EXTRACT TASK: {task_description}
    """
    return chain(task_description=description(task))


def compare_tasks(task: Task) -> bool:
    """
    COMPARE TASKS:
    1: {task}
    2: {task2}

    Are the tasks kind of equal?
    """
    return chain(task2=extract_task(task))


def test_extraction():
    task = Task(
        name="Do dishes",
        description="Do the dishes in the kitchen.",
        difficulty="easy",
        keywords=["kitchen", "dishes"],
    )

    assert compare_tasks(task)


if __name__ == "__main__":
    test_extraction()
