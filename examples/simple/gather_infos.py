from funcchain import chain, settings
from pydantic import BaseModel

# settings.llm = "ollama/openchat"
settings.console_stream = True


class Task(BaseModel):
    name: str
    description: str
    difficulty: str
    keywords: list[str]


def gather_infos(task_input: str) -> Task:
    """
    Based on this task input, gather all task infos.
    """
    return chain()


def plan_task(task: Task) -> str:
    """
    Based on the task infos, plan the task.
    """
    return chain()


def main() -> None:
    task_input = "I need to buy apples, oranges and bananas from whole foods"

    task = gather_infos(task_input)

    print("name:", task.name)
    print("description:", task.description)
    print("difficulty:", task.difficulty)
    print("keywords:", task.keywords)

    plan = plan_task(task)
    print("\nplan:", plan)


if __name__ == "__main__":
    main()
