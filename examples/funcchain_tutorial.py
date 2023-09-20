from funcchain import chain, settings
from langchain.pydantic_v1 import BaseModel, Field, validator


def say_hello(num: int) -> str:
    """
    Say hello in {num} different languages.
    """
    return chain()


answer = say_hello(3)
print("Say Hello: ", answer)


def language_analyse(text: str) -> str:
    """
    How many different languages are in {text}?
    """
    return chain()


analysis = language_analyse(answer)
print("Language Analyse: ", analysis)


class Analyse(BaseModel):
    languages: list[str] = Field(..., description="List of languages in the text")


def analyse(text: str) -> Analyse:
    """
    TEXT:
    {text}

    Return the languages in the text.
    """
    return chain()


analysis = analyse(answer)

print("Is Analyse: ", isinstance(analysis, Analyse))
print("Languages: ", analysis.languages)


class Task(BaseModel):
    task_name: str = Field(..., description="Name of the task")
    task_description: str = Field(..., description="Description of the task")
    difficulty: int = Field(..., description="Difficulty of the task (1-10)")

    @validator("difficulty")
    def validate_difficulty(cls, v):
        if v < 1 or v > 10:
            raise ValueError("Difficulty must be between 1 and 10")
        return v


def extract_task(text: str) -> Task:
    """
    TEXT:
    {text}

    Extract the task from the TEXT:
    """
    return chain()


task: Task = extract_task(
    "Do the following task:\n"
    "Create a new user and assign it to the admin group.\n"
    "This should be a really easy task."
)

print("Task: ", task.json(indent=2))
