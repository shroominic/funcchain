from pydantic import BaseModel
from funcchain import funcchain


class Task(BaseModel):
    name: str
    description: str
    difficulty: str
    keywords: list[str]


def gather_infos(task_input: str) -> Task:
    """
    TASK_INPUT:
    {task_input}

    Based on this task input, gather all task infos.
    """
    return funcchain()


def main():
    task_input = input("\nEnter task input: ")

    task = gather_infos(task_input)

    print("\nTASK:\n", task.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
