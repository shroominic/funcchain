from pydantic import BaseModel, field_validator

from funcchain import chain, settings

settings.retry_parse = 5


class Task(BaseModel):
    name: str
    difficulty: int
    keywords: list[str]

    @field_validator("keywords")
    def keywords_must_be_unique(cls, v: list[str]) -> list[str]:
        if len(v) != len(set(v)):
            raise ValueError("keywords must be unique")
        return v

    @field_validator("difficulty")
    def difficulty_must_be_between_1_and_10(cls, v: int) -> int:
        if v < 10 or v > 100:
            raise ValueError("difficulty must be between 10 and 100")
        return v


def gather_infos(user_description: str) -> Task:
    """
    Based on the user description,
    create a new task to put on the todo list.
    """
    return chain()


if __name__ == "__main__":
    task = gather_infos("cleanup the kitchen")
    print(f"{task=}")
