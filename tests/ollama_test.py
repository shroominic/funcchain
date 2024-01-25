import pytest
from funcchain import Image, chain, settings
from pydantic import BaseModel, Field


class Task(BaseModel):
    description: str
    difficulty: int


class TodoList(BaseModel):
    tasks: list[Task]


def todo_list(job_title: str) -> TodoList:
    """
    Create a todo list for a perfect day for the given job.
    """
    return chain()


@pytest.mark.skip_on_actions
def test_openhermes() -> None:
    settings.llm = "ollama/openhermes2.5-mistral"

    assert isinstance(
        todo_list("software engineer"),
        TodoList,
    )


@pytest.mark.skip_on_actions
def test_neural_chat() -> None:
    settings.llm = "ollama/openchat"

    assert isinstance(
        todo_list("ai engineer"),
        TodoList,
    )


class Analysis(BaseModel):
    description: str = Field(description="A description of the image")
    objects: list[str] = Field(description="A list of objects found in the image")


def analyse(image: Image) -> Analysis:
    """
    Analyse the image and extract its
    theme, description and objects.
    """
    return chain()


@pytest.mark.skip_on_actions
def test_vision() -> None:
    settings.llm = "ollama/bakllava"

    assert isinstance(
        analyse(Image.from_file("examples/assets/old_chinese_temple.jpg")),
        Analysis,
    )  # todo check actual output


# TODO: Test union types
# def test_union_types() -> None:
#     ...


def test_model_search_failure() -> None:
    settings.llm = "ollama/neural-chat-ultra-mega"

    try:
        todo_list("software engineer")
    except Exception:
        assert True
    else:
        assert False, "Model should not be found"


if __name__ == "__main__":
    test_openhermes()
    test_neural_chat()
    # test_vision()
    test_model_search_failure()
