import pytest
from pydantic import BaseModel

from funcchain import chain, settings


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
    settings.llm = "gguf/openhermes-2.5-mistral-7b"

    assert isinstance(
        todo_list("software engineer"),
        TodoList,
    )


@pytest.mark.skip_on_actions
def test_neural_chat() -> None:
    settings.llm = "gguf/neural-chat-7b-v3-1"

    assert isinstance(
        todo_list("ai engineer"),
        TodoList,
    )


# def test_vision() -> None:
#     from PIL import Image

#     settings.llm = "mys/ggml_llava-v1.5-13b"

#     class Analysis(BaseModel):
#         description: str = Field(description="A description of the image")
#         objects: list[str] = Field(description="A list of objects found in the image")

#     def analyse(image: Image.Image) -> Analysis:
#         """
#         Analyse the image and extract its
#         theme, description and objects.
#         """
#         return chain()

#     assert isinstance(
#         analyse(Image.open("examples/assets/old_chinese_temple.jpg")),
#         Analysis,
#     )

# TODO: Test union types
# def test_union_types() -> None:
#     ...


def test_model_search_failure() -> None:
    settings.llm = "gguf/neural-chat-ultra-mega"

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
