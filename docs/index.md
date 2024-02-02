<!-- markdownlint-disable MD033 MD046 -->
# Introduction

[![Version](https://badge.fury.io/py/funcchain.svg)](https://badge.fury.io/py/funcchain)
[![code-check](https://github.com/shroominic/funcchain/actions/workflows/code-check.yml/badge.svg)](https://github.com/shroominic/funcchain/actions/workflows/code-check.yml)
![Downloads](https://img.shields.io/pypi/dm/funcchain)
[![Discord](https://img.shields.io/discord/1192334452110659664?label=discord)](https://discord.gg/TrwWWMXdtR)
![PyVersion](https://img.shields.io/pypi/pyversions/funcchain)
[![Twitter Follow](https://img.shields.io/twitter/follow/shroominic?style=social)](https://x.com/shroominic)

`funcchain` is the _most pythonic_ way of writing cognitive systems. Leveraging pydantic models as output schemas combined with langchain in the backend allows for a seamless integration of llms into your apps.
It utilizes perfect with OpenAI Functions or LlamaCpp grammars (json-schema-mode) for efficient structured output.
In the backend it compiles the funcchain syntax into langchain runnables so you can easily invoke, stream or batch process your pipelines.

## Installation

<div class="termy">

```bash
$ pip install funcchain
---> 100%
```

</div>

!!! Important
    Make sure to have an OpenAI API key in your environment variables:

    ```bash
    export OPENAI_API_KEY="sk-rnUPxirSQ4bmz2He4qyaiKShdXJcsOsTg"
    ```
    (not needed for local models of course)

## Key Features

- 🐍 pythonic
- 🔀 easy swap between openai or local models
- 🔄 dynamic output types (pydantic models, or primitives)
- 👁️ vision llm support
- 🧠 langchain_core as backend
- 📝 jinja templating for prompts
- 🏗️ reliable structured output
- 🔁 auto retry parsing
- 🔧 langsmith support
- 🔄 sync, async, streaming, parallel, fallbacks
- 📦 gguf download from huggingface
- ✅ type hints for all functions and mypy support
- 🗣️ chat router component
- 🧩 composable with langchain LCEL
- 🛠️ easy error handling
- 🚦 enums and literal support
- 📐 custom parsing types

## Usage

```python
from funcchain import chain

def hello() -> str:
    """
    Say hello in 3 languages.
    """
    return chain()

print(hello()) # -> "Hallo, Bonjour, Hola"
```

This will call the OpenAI API and return the response.
Its using OpenAI since we did not specify a model and it will use the default model from the global settings of funcchain.

The underlying chat will look like this:

- User: "Say hello in 3 languages."
- AI: "Hallo, Bonjour, Hola"

The `chain()` function does all the magic in the background. It extracts the docstring, input arguments and return type of the function and compiles everything into a langchain prompt.

## Complex Example

Here a more complex example of what is possible. We create nested pydantic models and use union types to let the model choose the best shape to parse your given list into.

```python
from pydantic import BaseModel, Field
from funcchain import chain

# define nested models
class Item(BaseModel):
    name: str = Field(description="Name of the item")
    description: str = Field(description="Description of the item")
    keywords: list[str] = Field(description="Keywords for the item")

class ShoppingList(BaseModel):
    items: list[Item]
    store: str = Field(description="The store to buy the items from")

class TodoList(BaseModel):
    todos: list[Item]
    urgency: int = Field(description="The urgency of all tasks (1-10)")

# support for union types
def extract_list(user_input: str) -> TodoList | ShoppingList:
    """
    The user input is either a shopping List or a todo list.
    """
    return chain()

# the model will choose the output type automatically
lst = extract_list(
    input("Enter your list: ")
)

# custom handler based on type
match lst:
    case ShoppingList(items=items, store=store):
        print("Here is your Shopping List: ")
        for item in items:
            print(f"{item.name}: {item.description}")
        print(f"You need to go to: {store}")

    case TodoList(todos=todos, urgency=urgency):
        print("Here is your Todo List: ")
        for item in todos:
            print(f"{item.name}: {item.description}")
        print(f"Urgency: {urgency}")
```

The pydantic models force the language model to output only in the specified format. The actual ouput is a json string which is parsed into the pydantic model. This allows for a seamless integration of the language model into your app.
The union type selection works by listing every pydantic model as seperate function call to the model. So the LLM will select the best fitting pydantic model based on the prompt and inputs.
