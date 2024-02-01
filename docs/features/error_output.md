<!-- markdownlint-disable MD033 MD046 -->
# Example of raising an error

!!! Example
    error_output.py [Example](https://github.com/shroominic/funcchain/blob/main/examples/error_output.py)

    In this example, we will use the funcchain library to build a system that extracts user information from text.
    Most importantly we will be able to raise an error thats programmatically usable.
    You can adapt this for your own usage.

    The main functionality is to take a string of text and attempt to extract user information, such as name and email, and return a User object. If the information is insufficient, an Error is returned instead.

## Full Code Example

<pre><code id="codeblock">
```python
from funcchain import BaseModel, Error, chain
from rich import print

class User(BaseModel):
    name: str
    email: str | None

def extract_user_info(text: str) -> User | Error:
    """
    Extract the user information from the given text.
    In case you do not have enough infos, raise.
    """
    return chain()

print(extract_user_info("hey"))
# => returns Error

print(extract_user_info("I'm John and my mail is john@gmail.com"))
# => returns a User object

```
</code></pre>

Demo

<div class="termy">
    ```python
    $ extract_user_info("hey")

    Error(
        title='Invalid Input',
        description='The input text does not contain user information.'
    )

    $ extract_user_info("I'm John and my mail is john@gmail.com")

    User(
        name='John',
        email='john@gmail.com'
    )
    ```

</div>

## Instructions

!!! Step-by-Step

    **Necessary Imports**

    ```python
    from funcchain import BaseModel, Error, chain
    from rich import print
    ```

    **Define the User Model**

    ```python
    class User(BaseModel):
        name: str
        email: str | None
    ```
    The User class is a Pydantic model that defines the structure of the user information to be extracted, with fields for `name` and an email.
    Change the fields to experiment and alignment with your project.

    **Implement the Extraction Function**

    The `extract_user_info` function is intended to process the input text and return either a User object with extracted information or an Error if the information is not sufficient.

    ```python
    def extract_user_info(text: str) -> User | Error:
        """
        Extract the user information from the given text.
        In case you do not have enough infos, raise.
        """
        return chain()
    ```
    For experiments and adoptions also change the `str` that will be used in chain() to identify what you defined earlier in the `User(BaseModel)`


    **Run the Extraction System**

    This conditional block is used to execute the extraction function and print the results when the script is run directly.

    ```python
    print(extract_user_info("hey"))
    # => returns Error

    print(extract_user_info("I'm John and my mail is john@gmail.com"))
    # => returns a User object
    ```
