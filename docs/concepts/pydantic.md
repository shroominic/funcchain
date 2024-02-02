# Pydantic

`pydantic` is a python library for creating data structures with strict typing and automatic type validation.
When dealing with LLMs this is very useful because it exposes a precise `json-schema` that can be used with grammars or function-calling to force the LLM to respond in the desired way.
Additionally validation especially using custom validators can be used to automatically retry if the output does not match your requirements.

## BaseModel

When `from pydantic import BaseModel` this is imports the core class of Pydantic which can be used to construct your data structures.

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
    items: list[str]
```

This model can then be initiated:

```python
user = User(
    id=1943,
    name="Albert Hofmann",
    email="hofmann.albert@sandoz.ch",
    items=["lab coat", "safety glasses", "a bicycle"]
)
```

## Field Descriptions

To give the LLM more context about what you mean with the stucture you can provide field descriptions:

```python
from pydantic import Field

class User(BaseModel):
    id: int
    name: str = Field(description="FullName of the user.")
    email: str
    items: list[str] = Field(description="Everyday items of the user.")
```

These descriptions are included in the json-schema and are passed as format instructions into the prompt from the output parser.

## Custom Validators

You can also write custom validators if you want to check for specific information beyond just the type.

```python
from pydantic import field_validator

class User(BaseModel):
    id: int
    name: str = Field(description="FullName of the user.")
    email: str
    items: list[str] = Field(description="Everyday items of the user.")

    @field_validator("email")
    def keywords_must_be_unique(cls, v: str) -> str:
        if not v.endswith("@sandoz.ch"):
            raise ValueError("User has to work at Sandoz to register!")
        return v
```

In this example the validator makes sure every user has an email ending with `@sandoz.ch`.
