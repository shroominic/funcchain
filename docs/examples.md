# Examples

## Basic Usage

The `chain()` function allows you to call a prompt like a regular Python function. The docstring serves as the instructions and the return type annotation determines the output parsing.

```python
from funcchain import chain

def hello_world() -> str:
    """
    Generate a friendly hello world message.
    """
    return chain()

print(hello_world())
```

This will send the docstring to the AI assistant and parse the response as a string.

## Pydantic Models

You can use Pydantic models to validate the response.

```python
from funcchain import chain
from pydantic import BaseModel


class Message(BaseModel):
    text: str


def hello_message() -> Message:
    """
    Generate a message object that says hello.
    """
    return chain()


print(hello_message())
```

Now the response will be parsed as a Message object.

## Asynchronous Support

Async functions are also supported with `achain()`:

```python
import asyncio
from funcchain import achain

async def async_hello() -> str:
    """Say hello asynchronously"""
    return await achain()

print(asyncio.run(async_hello()))
```

This allows you to easily call AI functions from async code.

The funcchain project makes it really simple to leverage large language models in your Python code! Check out the source code for more examples.

## Advanced Examples

For advanced examples, checkout the examples directory [here](https://github.com/shroominic/funcchain/tree/main/examples)
