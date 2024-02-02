<!-- markdownlint-disable MD033 MD046 -->
# Retry Parsing

!!! Example
    [pydantic_validation.py](https://github.com/shroominic/funcchain/blob/main/examples/pydantic_validation.py)

    You can adapt this for your own usage.
    This serves as an example of how to implement data validation and task creation using pydantic for data models and funcchain for processing natural language input.

    The main functionality is to parse a user description, validate the task details, and create a new Task object with unique keywords and a difficulty level within a specified range.

## Full Code Example

<pre><code id="codeblock">
```python
from funcchain import chain, settings
from pydantic import BaseModel, field_validator

# settings.llm = "ollama/openchat"
settings.console_stream = True

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
```
</code></pre>

Demo

<div class="termy">
    ```python
    User:
    $ cleanup the kitchen

    task=Task
    name='cleanup',
    difficulty=30,
    keywords=['kitchen', 'cleanup']
    ```

</div>

## Instructions

!!! Step-by-Step
    **Necessary Imports**

    ```python
    from funcchain import chain, settings
    from pydantic import BaseModel, field_validator
    ```

    **Define the Task Model with Validators**
    The `Task` class is a Pydantic model with fields: `name`, `difficulty`, and `keywords`. Validators ensure data integrity:

    - `keywords_must_be_unique`: Checks that all keywords are distinct.
    - `difficulty_must_be_between_1_and_10`: Ensures difficulty is within 10 to 100.

    ```python
    class Task(BaseModel):
        name: str  # Task name.
        difficulty: int  # Difficulty level (10-100).
        keywords: list[str]  # Unique keywords.

        @field_validator("keywords")
        def keywords_must_be_unique(cls, v: list[str]) -> list[str]:
            # Ensure keyword uniqueness.
            if len(v) != len(set(v)):
                raise ValueError("keywords must be unique")
            return v

        @field_validator("difficulty")
        def difficulty_must_be_between_1_and_10(cls, v: int) -> int:
            # Validate difficulty range.
            if v < 10 or v > 100:
                raise ValueError("difficulty must be between 10 and 100")
            return v
    ```

    **Implement the Information Gathering Function**
    The gather_infos function is designed to take a user description and use the chain function to process and validate the input, returning a new Task object.
    Adjust the string description to match your purposes when changing the code above.

    ```python
    def gather_infos(user_description: str) -> Task:
        """
        Based on the user description,
        create a new task to put on the todo list.
        """
        return chain()
    ```

    **Execute the Script**
    Runs gather_infos with a sample and prints the Task.
    ```python
    if __name__ == "__main__":
        task = gather_infos("cleanup the kitchen")
        print(f"{task=}")
    ```
