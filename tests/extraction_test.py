from funcchain import BaseModel, achain, chain, settings

settings.temperature = 0
settings.llm = "gpt-3.5-turbo-1106"


class Task(BaseModel):
    name: str
    description: str
    difficulty: str
    keywords: list[str]

    def __str__(self) -> str:
        return self.model_dump_json(indent=2)


def description(task: Task) -> str:
    """
    Create a description of the task.
    """
    return chain()


async def extract_task(task_description: str) -> Task:
    """
    Extract the task based on the task description:
    {task_description}
    """
    return await achain()


def compare_tasks(task1: Task, task2: Task) -> bool:
    """
    Are the task1 and task2 similar?
    """
    return chain()


def test_extraction() -> None:
    from asyncio import run as _await

    task1 = Task(
        name="Do dishes",
        description="Do the dishes in the kitchen.",
        difficulty="easy",
        keywords=["kitchen", "dishes"],
    )

    task_description = description(task1)
    task2 = _await(extract_task(task_description))

    assert compare_tasks(task1, task2)


if __name__ == "__main__":
    test_extraction()
