from funcchain import BaseModel, achain, chain


class Task(BaseModel):
    name: str
    description: str
    difficulty: str
    keywords: list[str]

    def __str__(self) -> str:
        return self.json(indent=2)


def description(task: Task) -> str:
    """
    Create a description of the task.
    """
    return chain()


async def extract_task(task_description: str) -> Task:
    """
    EXTRACT TASK: {task_description}
    """
    return await achain()


def compare_tasks(task: Task, task2: Task) -> bool:
    """
    COMPARE TASKS:
    1: {task}
    2: {task2}

    Are the tasks kind of equal?
    """
    return chain()


def test_extraction() -> None:
    from asyncio import run as _await

    task = Task(
        name="Do dishes",
        description="Do the dishes in the kitchen.",
        difficulty="easy",
        keywords=["kitchen", "dishes"],
    )

    task_description = description(task)
    task2 = _await(extract_task(task_description))

    assert compare_tasks(task, task2)


if __name__ == "__main__":
    test_extraction()
