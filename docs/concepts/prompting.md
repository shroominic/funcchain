# Prompting

Prompting involes every text you write that the LLM recieves and interprets. It often involves `prompt engineering` which is optimizing and finetuning your wordings so the LLM understands what you wants and responds correctly.
Everything from the input argument names, output type and docstring are part of the prompt and are visible to the model to evaluate. Make sure your choose your terms well and try different wordings if you encounter problems.

## Jinja2 Templating

Often you can write your funcchains without templating but for special cases it is useful to do custom things.
Funcchain allows jinja2 as templating syntax for writing more complex prompts.
All function input areguments that are either `str` or a subclass of a `Pydantic Model` are awailable in the jinja environment and can be used.

```python
class GroceryList(BaseModel):
    recipie: str
    items: list[str]

def create_recipie(glist: GroceryList) -> str:
    """
    I want to cook {{ glist.recipie }}.
    Create a step by step recipie based on these ingridients I just bought:
    {% for i in glist.items %}
    - {{ i }}
    {% endfor %}
    """
    return chain()
```

The LLM will then recieve a formatted prompt based on what you input is.

## Input Argument Placement

If you do not specify a place in your prompt for your input arguments using jinja,
all unused arguments (`str` and `PydanticModels`) will then get automatically appended
to the beginning of your instruction.

E.g. if you just provide `Create a step by step recipie based on the grocery list.`,
the prompt template would look like this:

```html
<PromptTemplate>
    GLIST:
    {{ glist }}

    Create a step by step recipie based on the grocery list.
</PromptTemplate>
```

When inserting the instance of `GroceryList` into the template, the `__str__` method is called for converting the model into text. Keep this in mind if you want to customise apperence to the LLM.

## ChatModel Behavior

Keep in mind that funcchain in always using instructional chat prompting, so instrution is made the perspective of a Human <-> AI conversation. If you process input from your users its good to talk of them as `customers` so the model understands the perspective.
