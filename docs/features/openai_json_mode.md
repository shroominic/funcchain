<!-- markdownlint-disable MD033 MD046 -->
# JSON structured Output using Funcchain with OenAI

!!! Example
    See [openai_json_mode.py](https://github.com/shroominic/funcchain/blob/main/examples/openai_json_mode.py)

    This example will showcase how funcchain enables OpenAI to output even the type `int` as JSON.

    This example demonstrates using the funcchain library and pydantic to create a FruitSalad model, sum its contents, and output the total in a Result model as an integer.

## Full Code Example

<pre><code id="codeblock">
```python
from funcchain import chain
from pydantic import BaseModel

class FruitSalad(BaseModel):
    bananas: int = 0
    apples: int = 0

def sum_fruits(fruit_salad: FruitSalad) -> int:
    """
    Sum the number of fruits in a fruit salad.
    """
    return chain()

if __name__ == "__main__":
    fruit_salad = FruitSalad(bananas=3, apples=5)
    assert sum_fruits(fruit_salad) == 8
```
</code></pre>

Instructions
!!! Step-by-Step

    **Necessary Imports**

    `funcchain` for chaining functionality, and `pydantic` for the data models.

    ```python
    from funcchain import chain, settings
    from pydantic import BaseModel
    ```

    **Defining the Data Models**

    We define two Pydantic models: `FruitSalad` with integer fields for the number of bananas and apples.
    Of course feel free to change those classes according to your needs but use of `pydantic` is required.

    ```python
    class FruitSalad(BaseModel):
        bananas: int = 0
        apples: int = 0
    ```

    **Summing Function**

    The `sum_fruits` function is intended to take a `FruitSalad` object and use `chain()` for solving this task with an LLM. The result is returned then returned as integer.

    ```python
    def sum_fruits(fruit_salad: FruitSalad) -> int:
        """
        Sum the number of fruits in a fruit salad.
        """
        return chain()
    ```

    **Execution Block**

    ```python
    fruit_salad = FruitSalad(bananas=3, apples=5)
    assert sum_fruits(fruit_salad) == 8
    ```

    In the primary execution section of the script, we instantiate a `FruitSalad` object with predefined quantities of bananas and apples. We then verify that the `sum_fruits` function accurately calculates the total count of fruits, which should be 8 in this case.
