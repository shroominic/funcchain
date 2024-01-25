# funcchain

[![Version](https://badge.fury.io/py/funcchain.svg)](https://badge.fury.io/py/funcchain)
[![tests](https://github.com/shroominic/funcchain/actions/workflows/code-check.yml/badge.svg)](https://github.com/shroominic/funcchain/actions/workflows/code-check.yml)
![PyVersion](https://img.shields.io/pypi/pyversions/funcchain)
![Downloads](https://img.shields.io/pypi/dm/funcchain)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://docs.pydantic.dev/latest/contributing/#badges)
[![Twitter Follow](https://img.shields.io/twitter/follow/shroominic?style=social)](https://x.com/shroominic)

```bash
> pip install funcchain
```

## Introduction

`funcchain` is the *most pythonic* way of writing cognitive systems. Leveraging pydantic models as output schemas combined with langchain in the backend allows for a seamless integration of llms into your apps.
It works perfect with OpenAI Functions and soon with other models using JSONFormer.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ricklamers/funcchain-demo)

## Simple Demo

```python
from funcchain import chain
from pydantic import BaseModel

# define your output shape
class Recipe(BaseModel):
    ingredients: list[str]
    instructions: list[str]
    duration: int

# write prompts utilising all native python features
def generate_recipe(topic: str) -> Recipe:
    """
    Generate a recipe for a given topic.
    """
    return chain() # <- this is doing all the magic

# generate llm response
recipe = generate_recipe("christmas dinner")

# recipe is automatically converted as pydantic model
print(recipe.ingredients)
```

## Complex Structured Output

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

## Vision Models

```python
from funcchain import Image
from pydantic import BaseModel, Field
from funcchain import chain, settings

# set global llm using model identifiers (see MODELS.md)
settings.llm = "openai/gpt-4-vision-preview"

# everything defined is part of the prompt
class AnalysisResult(BaseModel):
    """The result of an image analysis."""

    theme: str = Field(description="The theme of the image")
    description: str = Field(description="A description of the image")
    objects: list[str] = Field(description="A list of objects found in the image")

# easy use of images as input with structured output
def analyse_image(image: Image.Image) -> AnalysisResult:
    """
    Analyse the image and extract its
    theme, description and objects.
    """
    return chain()

result = analyse_image(Image.open("examples/assets/old_chinese_temple.jpg"))

print("Theme:", result.theme)
print("Description:", result.description)
for obj in result.objects:
    print("Found this object:", obj)
```

## Seamless local model support

```python
from pydantic import BaseModel, Field
from funcchain import chain, settings

# auto-download the model from huggingface
settings.llm = "ollama/openchat"

class SentimentAnalysis(BaseModel):
    analysis: str
    sentiment: bool = Field(description="True for Happy, False for Sad")

def analyze(text: str) -> SentimentAnalysis:
    """
    Determines the sentiment of the text.
    """
    return chain()

# generates using the local model
poem = analyze("I really like when my dog does a trick!")

# promised structured output (for local models!)
print(poem.analysis)
```

## Features

- minimalistic and easy to use
- easy swap between openai and local models
- write prompts as python functions
- pydantic models for output schemas
- langchain core in the backend
- fstrings or jinja templates for prompts
- fully utilises OpenAI Functions or LlamaCpp Grammars
- langsmith support
- async and pythonic
- auto gguf model download from huggingface
- streaming support

## Documentation

Highly recommend to try out the examples in the `./examples` folder.

Coming soon... feel free to add helpful .md files :)

## Contribution

You want to contribute? That's great! Please run the dev setup to get started:

```bash
> git clone https://github.com/shroominic/funcchain.git && cd funcchain

> ./dev_setup.sh
```

Thanks!
