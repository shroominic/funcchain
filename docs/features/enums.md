<!-- markdownlint-disable MD033 MD046 -->
# Decision Making with Enums and Funcchain

!!! Example
    See [enums.py](https://github.com/shroominic/funcchain/blob/main/examples/enums.py)

    In this example, we will use the enum module and funcchain library to build a decision-making system.
    This is a useful task for creating applications that require predefined choices or responses.
    You can adapt this for your own usage.
    This serves as an example of how to implement decision-making logic using enums and the funcchain library.

## Full Code Example

A simple system that takes a question and decides a 'yes' or 'no' answer based on the input.

<pre><code id="codeblock">
```python
from enum import Enum
from funcchain import chain
from pydantic import BaseModel

class Answer(str, Enum):
    yes = "yes"
    no = "no"

class Decision(BaseModel):
    answer: Answer

def make_decision(question: str) -> Decision:
    """
    Based on the question decide yes or no.
    """
    return chain()

print(make_decision("Do you like apples?"))
```
</code></pre>

# Demo

<div class="termy">
    ```terminal
    $ make_decision("Do you like apples?")

    answer=<Answer.yes: 'yes'>
    ```
</div>

## Instructions

!!! Step-by-Step
    **Necessary Imports**

    ```python
    from enum import Enum
    from funcchain import chain
    from pydantic import BaseModel
    ```

    **Define the Answer Enum**

    The Answer enum defines possible answers as 'yes' and 'no', which are the only valid responses for the decision-making system. Experiment by using and describing other enums.

    ```python
    class Answer(str, Enum):
        yes = "yes"
        no = "no"
    ```

    **Create the Decision Model**

    The Decision class uses Pydantic to model a decision, ensuring that the answer is always an instance of the Answer enum.

    ```python
    class Decision(BaseModel):
        answer: Answer
    ```

    **Implement the Decision Function**

    The make_decision function is where the decision logic will be implemented, using `chain()` to process the question and return a decision.
    When using your own enums you want to edit this accordingly.

    ```python
    def make_decision(question: str) -> Decision:
        """
        Based on the question decide yes or no.
        """
        return chain()
    ```

    **Run the Decision System**

    This block runs the decision-making system, printing out the decision for a given question when the script is executed directly.


    ```python
    print(make_decision("Do you like apples?"))
    ```
