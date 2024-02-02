# Output Parser

## Output Type Hints

Funcchain recognises the output type hint you put on your function to automatically attach
a fitting output parser to the end of your chain. This makes it really to code because you just use normal python typing syntax and funcchain handles everything for your.

## Strings

The simplest output type is a string.
The output parser will return the content of the AI response just as it is.

## Pydantic Models

To force the model to respond in a certain way you can use pydantic models.
This gives your alot of flexibility and control over the output because you can define the exact types of your fields and even add custom validation logic. Everything of your defined model will be part of the prompt including model_name, class_docstring, field_names, field_types and field_descriptions.
This gives you alot of room for prompt engineering and optimisation.

```python
from funcchain import chain
from pydantic import BaseModel, Field

class GroceryList(BaseModel):
    recipie: str = Field(description="Goal of what to cook with all items.")
    items: list[str] = Field(description="Items to buy")

def create_grocerylist(customer_request: str) -> GroceryList
    """
    Come up with a grocery list based on what the customer wants.
    """
    return chain()
```

When calling this function with
e.g. `create_grocerylist("I want a cheap, protein rich and vegan meal.")`
the model is then forced to respond using the model as a json_schema
and the unterlying conversation would look like the following:

```html
<HumanMessage>
    CUSTOMER_REQUEST:
    I want a cheap, protein rich and vegan meal.

    Come up with a grocery list based on what the customer wants.
</HumanMessage>

<AIMessage>
    {
        "recipie": "lentil soup"
        "items" [
            "todo",
            "insert",
            "ingredients"
        ]
    }
</AIMessage>
```

This json is then automatically validated and parsed into the pydantic model.
When a validation fails the model automatically recieves the error as followup message and tries again.

## Primitive Types

You can also use other primitive types like int, float, bool, list, Literals, Enums, etc. </br>
Funcchain will then create a temporary pydantic model with the type as a single field and use that as the output parser.

```python
def create_grocerylist(customer_request: str) -> list[str]
    """
    Come up with a grocery list based on what the customer wants.
    """
    return chain()
```

This time when calling this function with
e.g. `create_grocerylist("I want a cheap, protein rich and vegan meal.")`
funcchain automatically creates a temporary pydantic model in the background like this:

```python
class Extract(BaseModel):
    value: list[str]
```

The model then understands the desired shape and will output like here:

```html
<AIMessage>
    {
        "value": [
            "todo",
            "insert",
            "ingredients"
        ]
    }
</AIMessage>
```

## Union Types

You can also use mupliple PydanticModels at once as the output type using Unions.
The LLM will then select one of the models that fits best your inputs.
Checkout the seperate page for [UnionTypes](unions.md) for more info.

## Streaming

You can stream everything with a `str` output type.

Since pydantic models need to be fully constructed before they can be returned, you can't use them for streaming.
There is one approach to stream pydantic models but it works only if all fields are Optional, which is not the case for most models and they still come field by field.

This is not implemented yet but will be added in the future.
