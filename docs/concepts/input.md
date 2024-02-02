# Input Arguments

Funcchain utilises your function's input arguments including type hints to compile your prompt.
You can utilise the following types:

## Strings

All string inputs serve as classic prompt placeholders and are replaced with the input value.
You can insert anything as long as you cast it to a string and the language model will see its as text.

```python
def create_username(full_name: str, email: str) -> str:
    """
    Create a creative username from the given full name and email.
    """
    return chain()
```

All strings that are not mentioned in the instructions are automatically added to the beginning of the prompt.

When calling `create_username("John Doe", "john.doe@gmail.com")` the compiled prompt will look like this:

```html
<HumanMessage>
    FULL_NAME:
    John Doe

    EMAIL:
    john.doe@gmail.com

    Create a creative username from the given full name and email.
</HumanMessage>
```

The language model will then be able to use the input values to generate a good username.

You can also manually format your instructions if you want to have more control over the prompt.
Use jinja2 syntax to insert the input values.

```python
def create_username(full_name: str, email: str) -> str:
    """
    Create a creative username for {{ full_name }} with the mail {{ email }}.
    """
    return chain()
```

Compiles to:

```html
<HumanMessage>
    Create a creative username for John Doe with the mail john.doe@gmail.com.
</HumanMessage>
```

## Pydantic Models

You can also use pydantic models as input arguments.
This is useful if you already have complex data structures that you want to use as input.

```python
class User(BaseModel):
    full_name: str
    email: str

def create_username(user: User) -> str:
    """
    Create a creative username from the given user.
    """
    return chain()
```

By default, the pydantic model is converted to a string using the `__str__` method
and then added to the prompt.

```html
<HumanMessage>
    USER:
    full_name='Herbert Geier' email='hello@bert.com'

    Create a creative username from the given user.
</HumanMessage>
```

If you want more control you can override the `__str__` method of your pydantic model.
Or use jinja2 syntax to manually unpack the model.

```python
class User(BaseModel):
    full_name: str
    email: str

def create_username(user: User) -> str:
    """
    Create a creative username for {{ user.full_name }} with the mail {{ user.email }}.
    """
    return chain()
```

## Images

todo: write

## Other Types

More special types are coming soon.

## Important Notes

You need to use type hints for all your input arguments.
Otherwise, funcchain will just ignore them.
