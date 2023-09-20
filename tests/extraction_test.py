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


def extract_task(task_description: Task) -> Task:
    """
    EXTRACT TASK: {task_description}
    """
    return chain()


def compare_tasks(task: Task, task2: Task) -> bool:
    """
    COMPARE TASKS:
    1: {task}
    2: {task2}

    Are the tasks kind of equal?
    """
    return chain()


def test_extraction():
    task = Task(
        name="Do dishes",
        description="Do the dishes in the kitchen.",
        difficulty="easy",
        keywords=["kitchen", "dishes"],
    )

    task_description = description(task)
    task2 = extract_task(task_description)

    assert compare_tasks(task, task2)


if __name__ == "__main__":
    test_extraction()
