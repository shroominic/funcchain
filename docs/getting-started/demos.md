<!-- markdownlint-disable MD033 MD046 -->
# Demos

## Simple Structured Output

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
    def generate_recipe(topic: str) -> Recipe:
        """
        Generate a recipe for a given topic.
        """
        return chain()
    ```
    In this example the `generate_recipe` function takes a topic string and returns a `Recipe` instance for that topic.
    # Understanding chain() Functionality
    Chain() is the backend magic of funcchain. Behind the szenes it creates the llm function from the function signature and docstring.
    Meaning it will turn your function into usable LLM input.

    The `chain()` function is the core component of funcchain. It takes the docstring, input arguments and return type of the function and compiles everything into a langchain runnable . It then executes the prompt with your input arguments if you call the function and returns the parsed result.

    # Print your response
    ```python
    recipe = generate_recipe("christmas dinner")

    print(recipe.ingredients)
    ```

### Demo

<div class="termy">
    ```
    $ print(generate_recipe("christmas dinner").ingredients

    ['turkey', 'potatoes', 'carrots', 'brussels sprouts', 'cranberry sauce', 'gravy','butter', 'salt', 'pepper', 'rosemary']

    ```
</div>

## Complex Structured Output

([full code](../index.md#complex-example))

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

    In this example, we create a more complex data structure with nested models.
    The Item model defines the attributes of a single item, such as its name, description, and keywords.
    ShoppingList and TodoList models define the attributes of a shopping list and a todo list, utilizing the Item model as a nested model.

    You can define new Pydantic models or extend existing ones by adding additional fields or methods. The general approach is to identify the data attributes relevant to your application and create corresponding model classes with these attributes.

    The Field descriptions serve as prompts for the language model to understand the data structure.
    Additionally you can include a docstring for each model class to provide further information to the LLM.

    !!! Important
        Everything including class names, argument names, doc string and field descriptions are part of the prompt and can be optimised using prompting techniques.


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
    lst = extract_list("Complete project report, Prepare for meeting, Respond to emails")
    ```

    **Define your custom handlers**

    And now its time to define what happens with the result.
    You can then use the lst (list) variable to access the attributes of the list.
    It utilizes pattern matching to determine the type of list and print the corresponding output.

    ```python
    match lst:
        case ShoppingList(items=items, store=store):
            print("Shopping List: ")
            for item in items:
                print(f"{item.name}: {item.description}")
            print(f"You need to go to: {store}")

        case TodoList(todos=todos, urgency=urgency):
            print("Todo List: ")
            for item in todos:
                print(f"{item.name}: {item.description}")
            print(f"Urgency: {urgency}")
    ```

<div class="termy">
    ```
    $ extract_list("Complete project report, Prepare for meeting, Respond to emails")

    Todo List:
    Complete project report: Finish the project report and submit it
    Prepare for meeting: Gather all necessary materials and information for the meeting
    Respond to emails: Reply to all pending emails
    Urgency: 8
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

<div class="termy">
    ```
    result = analyse_image(
        Image.from_file("examples/assets/old_chinese_temple.jpg")
    )

    print("Theme:", result.theme)
    print("Description:", result.description)
    for obj in result.objects:
        print("Found this object:", obj)

    $ ..................

    Theme: Traditional Japanese architecture and nature during rainfall
    Description: The image depicts a serene rainy scene at night in a traditional Japanese setting. A two-story wooden building with glowing green lanterns is the focal point, surrounded by a cobblestone path, a blooming pink cherry blossom tree, and a stone lantern partially obscured by the rain. The atmosphere is tranquil and slightly mysterious.
    Found this object: building
    Found this object: green lanterns
    Found this object: cherry blossom tree
    Found this object: rain
    Found this object: cobblestone path
    Found this object: stone lantern
    Found this object: wooden structure

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
    settings.llm = "llamacpp/openchat-3.5-0106:Q3_K_M"
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
    poem = analyze("I really like when my dog does a trick!")
    print(poem.analysis)
    ```

!!! Useful

    For seeing whats going on inside the LLM you should try the Langsmith integration:
    Add those lines to .env and funcchain will use langsmith tracing.

    ```bash
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_API_KEY="ls__api_key"
    LANGCHAIN_PROJECT="PROJECT_NAME"
    ```

    Langsmith is used to understand what happens under the hood of your LLM generations.
    When multiple LLM calls are used for an output they can be logged for debugging.
