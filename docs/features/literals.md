<!-- markdownlint-disable MD033 MD046 -->
# Literal Type Enforcement in Funcchain

!!! Example
    literals.py [Example](https://github.com/shroominic/funcchain/blob/main/examples/literals.py)

    This is a useful task for scenarios where you want to ensure that certain outputs strictly conform to a predefined set of values.
    This serves as an example of how to implement strict type checks on outputs using the Literal type from the typing module and the funcchain library.

    You can adapt this for your own usage.

## Full Code Example

<pre><code id="codeblock">
```python
from typing import Literal
from funcchain import chain
from pydantic import BaseModel

class Ranking(BaseModel):
    analysis: str
    score: Literal[11, 22, 33, 44, 55]
    error: Literal["no_input", "all_good", "invalid"]

def rank_output(output: str) -> Ranking:
    """
    Analyze and rank the output.
    """
    return chain()

rank = rank_output("The quick brown fox jumps over the lazy dog.")
print(rank)
```
</code></pre>

Demo

<div class="termy">
    ```python
    rank = rank_output("The quick brown fox jumps over the lazy dog.")
    print(rank)
    $ ........
    Ranking(analysis='...', score=33, error='all_good')
    ```
</div>

## Instructions

!!! Step-by-Step

    **Necessary Imports**

    ```python
    from typing import Literal
    from funcchain import chain
    from pydantic import BaseModel
    ```

    **Define the Ranking Model**

    The Ranking class is a Pydantic model that uses the Literal type to ensure that the score and error fields can only contain certain predefined values.
    So experiment with changing those but keeping this structure of the class.
    The LLM will be forced to deliver one of the defined output.

    ```python
    class Ranking(BaseModel):
        analysis: str
        score: Literal[11, 22, 33, 44, 55]
        error: Literal["no_input", "all_good", "invalid"]
    ```

    **Implement the Ranking Function**

    Use `chain()` to process a user input, which must be a string.
    Adjust the content based on your above defined class.

    ```python
    def rank_output(output: str) -> Ranking:
     """
     Analyze and rank the output.
     """
     return chain()
    ```

    **Execute the Ranking System**

    This block is used to execute the ranking function and print the results when the script is run directly.

    ```python
    rank = rank_output("The quick brown fox jumps over the lazy dog.")
    print(rank)
    ```
