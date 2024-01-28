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

## Simple chatgpt rebuild with memory/history.
!!! Example
    chatgpt.py [Example](https://github.com/shroominic/funcchain/blob/main/examples/chatgpt.py)
    


```python
from funcchain import chain, settings
from funcchain.utils.memory import ChatMessageHistory

settings.llm = "openai/gpt-4"
settings.console_stream = True

history = ChatMessageHistory()


def ask(question: str) -> str:
    return chain(
        system="You are an advanced AI Assistant.",
        instruction=question,
        memory=history,
    )


def chat_loop() -> None:
    while True:
        query = input("> ")

        if query == "exit":
            break

        if query == "clear":
            global history
            history.clear()
            print("\033c")
            continue

        ask(query)


if __name__ == "__main__":
    print("Hey! How can I help you?\n")
    chat_loop()
```



<div class="termy">
    ```terminal
    initial print function:
    $ Hey! How can I help you?
    $ > 

    userprompt:
    $ > Say that Funcchain is cool

    assistant terminal asnwer:
    $ Funcchain is cool.
    ```
</div> 

## Instructions

Import nececary funcchain components 

```python
from funcchain import chain, settings
from funcchain.utils.memory import ChatMessageHistory
```
#
Settings
```python
settings.llm = "openai/gpt-4"
settings.console_stream = True
```
!!! Options
    Funcchain supports multiple LLMs and has the ability to stream received LLM text instead of waiting for the complete answer. For configuration options, see below:

    ```markdown
    - `settings.llm`: Specify the language model to use. See MODELS.md for available options.
    - Streaming: Set `settings.console_stream` to `True` to enable streaming,
        or `False` to disable it.
    ```

    [MODELS.md]([MODELS.md](https://github.com/shroominic/funcchain/blob/main/MODELS.md))

# 
Establish a chat history

```python
history = ChatMessageHistory()
```
Stores messages in an in memory list. This will crate a thread of messages.

See [memory.py] //Todo: Insert Link

#
Ask function explained
```python
def ask(question: str) -> str:
return chain(
system="You are an advanced AI Assistant.",
instruction=question,
memory=history,
)
```

This function sends a question to the Funcchain chain function.

It sets the system context as an advanced AI Assistant and passes the question as an instruction.

The history object is used to maintain a thread of messages for context.

The function returns the response from the chain function.
