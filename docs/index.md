# Getting Started

[![Version](https://badge.fury.io/py/funcchain.svg)](https://badge.fury.io/py/funcchain)
[![code-check](https://github.com/shroominic/funcchain/actions/workflows/code-check.yml/badge.svg)](https://github.com/shroominic/funcchain/actions/workflows/code-check.yml)
![Downloads](https://img.shields.io/pypi/dm/funcchain)
[![Discord](https://img.shields.io/discord/1192334452110659664?label=discord)](https://discord.gg/TrwWWMXdtR)
![License](https://img.shields.io/pypi/l/funcchain)
![PyVersion](https://img.shields.io/pypi/pyversions/funcchain)

## Welcome

!!! Description
    funcchain is the *most pythonic* way of writing cognitive systems. Leveraging pydantic models as output schemas combined with langchain in the backend allows for a seamless integration of llms into your apps.
    It works perfect with OpenAI Functions and soon with other models using JSONFormer.

Key features:

- increased productivity
- prompts as Python functions
- pydantic models as output schemas
- langchain schemas in the backend
- fstrings or jinja templates for prompts
- fully utilises OpenAI Functions
- minimalistic and easy to use

## Installation

<div class="termy">

```bash
$ pip install funcchain
---> 100%
```

</div>

!!! Important
    Make sure to have an OpenAI API key in your environment variables. For example,

```bash
export OPENAI_API_KEY=sk-**********
```

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
