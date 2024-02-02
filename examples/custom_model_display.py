from funcchain import chain
from pydantic import BaseModel


class Task(BaseModel):
    name: str
    description: str
    difficulty: int

    def __str__(self) -> str:
        return f"{self.name}\n - {self.description}\n - Difficulty: {self.difficulty}"


def plan_task(task: Task) -> str:
    """
    Based on the task infos, plan the task step by step.
    """
    return chain()


if __name__ == "__main__":
    task = Task(
        name="Do Laundry",
        description="Collect and wash all the dirty clothes.",
        difficulty=4,
    )
    print(plan_task(task))
