# funcchain

```bash
> pip install funcchain
```

## Introduction

`funcchain` is the *most pythonic* way of writing cognitive systems. Leveraging pydantic models as output schemas combined with langchain in the backend allows for a seamless integration of llms into your apps.
It works perfect with OpenAI Functions and soon with other models using JSONFormer.

## Demo

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ricklamers/funcchain-demo)

```python
from typing import Union, List
from langchain.pydantic_v1 import BaseModel, Field
from funcchain import chain

class Item(BaseModel):
    name: str = Field(..., description="Name of the item")
    description: str = Field(..., description="Description of the item")
    keywords: List[str] = Field(..., description="Keywords for the item")

class ShoppingList(BaseModel):
    """ List of items to buy """
    items: List[Item]
    store: str = Field(..., description="The store to buy the items from")

class TodoList(BaseModel):
    todos: List[Item]
    urgency: int = Field(..., description="The urgency of all tasks (1-10)")

def extract_list(user_input: str) -> Union[TodoList, ShoppingList]:
    """
    USER_INPUT:
    {user_input}

    The user input is either a shopping List or a todo list.
    """
    return chain()


user_input = input("Enter your list: ")
lst = extract_list(user_input)

if isinstance(lst, ShoppingList):
    print("Here is your Shopping List: ")
    for item in lst.items:
        print(f"{item.name}: {item.description}")
    print(f"You need to go to: {lst.store}")

if isinstance(lst, TodoList):
    print("Here is your Todo List: ")
    for item in lst.todos:
        print(f"{item.name}: {item.description}")
    print(f"Urgency: {lst.urgency}")

```

## Features

- increased productivity
- prompts as Python functions
- pydantic models as output schemas
- langchain schemas in the backend
- fstrings or jinja templates for prompts
- fully utilises OpenAI Functions
- minimalistic and easy to use
- langsmith support
- async support

## Documentation

Coming soon and feel free to contribute

## Contribution

You want to contribute? That's great! Please run the dev setup to get started:

```bash
> git clone https://github.com/shroominic/funcchain.git && cd funcchain

> ./dev_setup.sh
```
