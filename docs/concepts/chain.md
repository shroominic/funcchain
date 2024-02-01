# Chain

## `chain()`

The chain function abstracts away all the magic happening in the funcchain backend. It extracts the docstring, input arguments and return type of the function and compiles everything into a langchain prompt.

```python
from funcchain import chain

def ask(question: str) -> str:
    """
    Answer the given question.
    """
    return chain()

ask("What is the capital of Germany?")
# => "The capital of Germany is Berlin."
```

## `achain()`

Async version of the `chain()` function.

```python
import asyncio
from funcchain import achain

async def ask(question: str) -> str:
    """
    Answer the given question.
    """
    return await achain()

asyncio.run(ask("What is the capital of Germany?"))
# => "The capital of Germany is Berlin."
```

## `@runnable`

The `@runnable` decorator is used to compile a chain function into a langchain runnable object.
You just write a normal funcchain function using chain() and then decorate it with `@runnable`.

```python
from funcchain import chain, runnable

@runnable
def ask(question: str) -> str:
    """
    Answer the given question.
    """
    return chain()

ask.invoke(input={"question": "What is the capital of Germany?"})
# => "The capital of Germany is Berlin."
```
