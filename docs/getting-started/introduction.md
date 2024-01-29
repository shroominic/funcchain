[![Version](https://badge.fury.io/py/funcchain.svg)](https://badge.fury.io/py/funcchain)
[![tests](https://github.com/shroominic/funcchain/actions/workflows/code-check.yml/badge.svg)](https://github.com/shroominic/funcchain/actions/workflows/code-check.yml)
![PyVersion](https://img.shields.io/pypi/pyversions/funcchain)
![Downloads](https://img.shields.io/pypi/dm/funcchain)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://docs.pydantic.dev/latest/contributing/#badges)
[![Twitter Follow](https://img.shields.io/twitter/follow/shroominic?style=social)](https://x.com/shroominic)

<div class="termy">

    ```bash
    $ pip install funcchain
    ---> 100%
    ```

</div>

!!! Useful: Langsmith integration

    Add those lines to .env and funcchain will use langsmith tracing.

    ```bash
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_API_KEY="ls__api_key"
    LANGCHAIN_PROJECT="PROJECT_NAME"
    ```

    Langsmith is used to understand what happens under the hood of your LLM generations.
    When multiple LLM calls are used for an output they can be logged for debugging.

## Introduction

`funcchain` is the _most pythonic_ way of writing cognitive systems. Leveraging pydantic models as output schemas combined with langchain in the backend allows for a seamless integration of llms into your apps.
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

!!! Step-by-Step
    ```python
    # define your output shape
    class Recipe(BaseModel):
        ingredients: list[str]
        instructions: list[str]
        duration: int

```

    A Recipe class is defined, inheriting from BaseModel (pydantic library). This class
    specifies the structure of the output data, which you can customize.
    In the example it includes a list of ingredients, a list of instructions, and an integer
    representing the duration

    ```python
    # write prompts utilising all native python features
    def generate_recipe(topic: str) -> Recipe:
        """
        Generate a recipe for a given topic.
        """
        return chain() # <- this is doing all the magic
    ```
    In this example the `generate_recipe` function takes a topic string and returns a `Recipe` instance for that topic.
    # Understanding chain() Functionality
    Chain() is the backend magic of funcchain. Behind the szenes it creates the prompt executable from the function signature.
    Meaning it will turn your function into usable LLM input.

    The `chain()` function does the interaction with the language model to generate a recipe. It accepts several parameters: `system` to specify the model, `instruction` for model directives, `context` to provide relevant background information, `memory` to maintain conversational state, `settings_override` for custom settings, and `**input_kwargs` for additional inputs. Within `generate_recipe`, `chain()` is called with arguments derived from the function's parameters, the function's docstring, or the library's default settings. It compiles these into a Runnable, which then prompts the language model to produce the output. This output is automatically structured into a `Recipe` instance, conforming to the Pydantic model's schema.

    # Get your response
    ```python
    # generate llm response
    recipe = generate_recipe("christmas dinner")

    # recipe is automatically converted as pydantic model
    print(recipe.ingredients)
    ```

## Demo

<div class="termy">
    ```
    $ print(generate_recipe("christmas dinner").ingredients

    ['turkey', 'potatoes', 'carrots', 'brussels sprouts', 'cranberry sauce', 'gravy',
    'butter', 'salt', 'pepper', 'rosemary']

    ```
</div>

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

!!! Step-by-Step
    **Nececary Imports**

    ```python
    from pydantic import BaseModel, Field
    from funcchain import chain
    ```

    **Data Structures and Model Definitions**
    ```python
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

    ```

    In this example, Funcchain utilizes Pydantic models to create structured data schemas that facilitate the processing of programmatic inputs.

    You can define new Pydantic models or extend existing ones by adding additional fields or methods. The general approach is to identify the data attributes relevant to your application and create corresponding model classes with these attributes.


    **Union types**
    ```python
    # support for union types
    def extract_list(user_input: str) -> TodoList | ShoppingList:
        """
        The user input is either a shopping List or a todo list.
        """
        return chain()
    ```
    The extract_list function uses the chain function to analyze user input and return a structured list:
    In the example:
    - Union Types: It can return either a TodoList or a ShoppingList, depending on the input.
    - Usage of chain: chain simplifies the process, deciding the type of list to return.

    For your application this is going to serve as a router to route between your previously defined models.

    **Get a list from the user** (here as "lst")
    ```python
    # the model will choose the output type automatically
    lst = extract_list(
        input("Enter your list: ")
    )

    ```

    **Define your custom handlers**

    And now its time to define what happens with the result.
    You can then use the lst variable to match.

    ```python
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

<div class="termy">
    ```
    lst = extract_list(
        input("Enter your list: ")
    )

    User:
    $ Complete project report, Prepare for meeting, Respond to emails;
    $ if I don't respond I will be fired

    Output:
    $ ...............
    Here is your Todo List:
    Complete your buisness tasks: project report, Prepare for meeting, Respond to emails
    Urgency: 10
    //add real output
    ```

</div>

## Vision Models

```python
from PIL import Image
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

!!! Step-by-Step
    **Nececary Imports**

    ```python
    from PIL import Image
    from pydantic import BaseModel, Field
    from funcchain import chain, settings
    ```

    **Define Model**
    set global llm using model identifiers see [MODELS.md](https://github.com/shroominic/funcchain/blob/main/MODELS.md)
    ```python
    settings.llm = "openai/gpt-4-vision-preview"
    ```
    Funcchains modularity allows for all kinds of models including local models


    **Analize Image**
    Get structured output from an image in our example `theme`, `description` and `objects`
    ```python
    # everything defined is part of the prompt
    class AnalysisResult(BaseModel):
        """The result of an image analysis."""

        theme: str = Field(description="The theme of the image")
        description: str = Field(description="A description of the image")
        objects: list[str] = Field(description="A list of objects found in the image")
    ```
    Adjsut the fields as needed. Play around with the example, feel free to experiment.
    You can customize the analysis by modifying the fields of the `AnalysisResult` model.

    **Function to start the analysis**

    ```python
    # easy use of images as input with structured output
    def analyse_image(image: Image.Image) -> AnalysisResult:
        """
        Analyse the image and extract its
        theme, description and objects.
        """
        return chain()
    ```
    Chain() will handle the image input.
    We here define again the fields from before `theme`, `description` and `objects`

    give an image as input `image: Image.Image`

    Its important that the fields defined earlier are mentioned here with the prompt
    `Analyse the image and extract its`...

## Demo

<div class="termy">
    ```
    print(analyse_image(image: Image.Image))

    $ ..................

    Theme: Nature
    Description: A beautiful landscape with a mountain range in the background, a clear blue sky, and a calm lake in the foreground surrounded by greenery.
    Found this object: mountains
    Found this object: sky
    Found this object: lake
    Found this object: trees
    Found this object: grass

    ```

</div>

## Seamless local model support

Yes you can use funcchain without internet connection.
Start heating up your device.

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

!!! Step-by-Step
    **Nececary Imports**

    ```python
    from pydantic import BaseModel, Field
    from funcchain import chain, settings

```

    **Choose and enjoy**
    ```python
    # auto-download the model from huggingface
    settings.llm = "ollama/openchat"
    ```

    **Structured output definition**
    With an input `str` a description can be added to return a boolean `true` or `false`
    ```python
    class SentimentAnalysis(BaseModel):
    analysis: str
    sentiment: bool = Field(description="True for Happy, False for Sad")
    ```
    Experiment yourself by adding different descriptions for the true and false case.

    **Use `chain()` to analize**
    Defines with natural language the analysis
    ```python
    def analyze(text: str) -> SentimentAnalysis:
    """
    Determines the sentiment of the text.
    """
    return chain()
    ```
    For your own usage adjust the str. Be precise and reference your classes again.

    **Generate and print the output**
    ```python
    **Use the analyze function and print output**

    # generates using the local model
    poem = analyze("I really like when my dog does a trick!")

    # promised structured output (for local models!)
    print(poem.analysis)
    ```

# Demo

<div class="termy">
    ```
    poem = analyze("I really like when my dog does a trick!")

    $ ..................

    Add demo

    ```
</div>

## Features

- **🎨 Minimalistic and Easy to Use**: Designed with simplicity in mind for straightforward usage.
- **🔄 Model Flexibility**: Effortlessly switch between OpenAI and local models.
- **📝 Pythonic Prompts**: Craft natural language prompts as intuitive Python functions.
- **🔧 Structured Output**: Define output schemas with Pydantic models.
- **🚀 Powered by LangChain**: Utilize the robust LangChain core for backend operations.
- **🧩 Template Support**: Employ f-strings or Jinja templates for dynamic prompt creation.
- **🔗 Integration with AI Services**: Take full advantage of OpenAI Functions or LlamaCpp Grammars.
- **🛠️ Langsmith Support**: Ensure compatibility with Langsmith for superior language model interactions.
- **⚡ Asynchronous and Pythonic**: Embrace modern Python async features.
- **🤗 Huggingface Integration**: Automatically download models from Huggingface.
- **🌊 Streaming Support**: Enable real-time streaming for interactive applications.

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
