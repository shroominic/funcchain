# Errors

## Example

```python
from funcchain import BaseModel, Error, chain
from rich import print

class User(BaseModel):
    name: str
    email: str | None

def extract_user_info(text: str) -> User | Error:
    """
    Extract the user information from the given text.
    In case you do not have enough infos, return an error.
    """
    return chain()

print(extract_user_info("hey what's up?"))
# => Error(title='Invalid Input', description='The input text does not contain user information.')

print(extract_user_info("I'm John and my email is john@mail.com"))
# => User(name='John', email='john@mail.com')
```

## Error Type

(currently only supported for union output types e.g. `Answer | Error` so only openai models)

The Error type is a special type that can be used to return an error from a chain function.
It is just a pydantic model with a title and description field.

```python
class Error(BaseModel):
    """
    Fallback function for invalid input.
    If you are unsure on what function to call, use this error function as fallback.
    This will tell the user that the input is not valid.
    """

    title: str = Field(description="CamelCase Name titeling the error")
    description: str = Field(..., description="Short description of the unexpected situation")

    def __raise__(self) -> None:
        raise Exception(self.description)
```

You can also create your own error types by inheriting from the Error type.
Or just do it similar to the example above.
