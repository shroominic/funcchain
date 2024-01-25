from funcchain import chain, settings
from pydantic import BaseModel, Field


class Task(BaseModel):
    name: str
    description: str


class TodoList(BaseModel):
    tasks: list[Task]


def todo_list(job_title: str) -> TodoList:
    """
    Create a todo list for a perfect day for the given job.
    """
    return chain()


def test_gpt_35_turbo() -> None:
    settings.llm = "openai/gpt-3.5-turbo"

    assert isinstance(
        todo_list("software engineer"),
        TodoList,
    )


def test_gpt4() -> None:
    settings.llm = "openai/gpt-4"

    assert isinstance(
        todo_list("software engineer"),
        TodoList,
    )


def test_vision() -> None:
    from funcchain import Image

    settings.llm = "openai/gpt-4-vision-preview"

    class Analysis(BaseModel):
        description: str = Field(description="A description of the image")
        objects: list[str] = Field(description="A list of objects found in the image")

    def analyse(image: Image) -> Analysis:
        """
        Analyse the image and extract its
        theme, description and objects.
        """
        return chain()

    assert isinstance(
        analyse(Image.from_file("examples/assets/old_chinese_temple.jpg")),
        Analysis,
    )


if __name__ == "__main__":
    test_gpt_35_turbo()
    test_gpt4()
    test_vision()
