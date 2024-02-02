# Usage

To write your cognitive architectures with the funcchain syntax you need to import the `chain` function from the `funcchain` package.

```python
from funcchain import chain
```

This chain function it the core component of funcchain.
It takes the docstring, input arguments and return type of the function and compiles everything into a langchain prompt.
It then executes the prompt with your input arguments if you call the function and returns the parsed result.

```python
def hello(lang1: str, lang2: str, lang3: str) -> list[str]:
    """
    Say hello in these 3 languages.
    """
    return chain()

hello("German", "French", "Spanish")
```

The underlying chat in the background will look like this:

```html
<HumanMessage>
LANG1: German
LANG2: French
LANG3: Spanish

Say hello in these 3 languages.
</HumanMessage>

<AIMessage>
{
    "value": ["Hallo", "Bonjour", "Hola"]
}
</AIMessage>
```

Funcchain is handling all the redundant and complicated structuring of your prompts so you can focus on the important parts of your code.

All input arguments are automatically added to the prompt so the model has context about what you insert.
The return type is used to force the model using a json-schema to always return a json object in the desired shape.
