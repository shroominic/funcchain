<!-- markdownlint-disable MD033 MD046 -->
# Different LLMs with funcchain EASY TO USE

!!! Example
    See [ollama.py](https://github.com/shroominic/funcchain/blob/main/examples/ollama.py)
    Also see supported [MODELS.md](https://github.com/shroominic/funcchain/blob/main/MODELS.md)

    In this example, we will use the funcchain library to perform sentiment analysis on a piece of text. This showcases how funcchain can seamlessly utilize different Language Models (LLMs) from ollama, without many unnececary code changes..

    This is particularly useful for developers looking to integrate different models in a single application or just experimenting with different models.

## Full Code Example

<pre><code id="codeblock">
```python
from funcchain import chain, settings
from pydantic import BaseModel, Field

# define your model
class SentimentAnalysis(BaseModel):
    analysis: str = Field(description="A description of the analysis")
    sentiment: bool = Field(description="True for Happy, False for Sad")

# define your prompt
def analyze(text: str) -> SentimentAnalysis:
    """
    Determines the sentiment of the text.
    """
    return chain()

if __name__ == "__main__":
    # set global llm
    settings.llm = "ollama/openchat"

    # log tokens as stream to console
    settings.console_stream = True

    # run prompt
    poem = analyze("I really like when my dog does a trick!")

    # show final parsed output
    print(poem)
```
</code></pre>

# Demo

<div class="termy">
    ```
    poem = analyze("I really like when my dog does a trick!")

    $ {"analysis": "A dog trick", "sentiment": true}

    SentimentAnalysis(analysis='A dog trick', sentiment=True)

    ```
</div>

## Instructions

!!! Step-by-Step

    **Necessary Imports**

    ```python
    from funcchain import chain, settings
    from pydantic import BaseModel, Field
    ```

    **Define the Data Model**
    Here, we define a `SentimentAnalysis` model with a description of the sentiment analysis and a boolean field indicating the sentiment.

    ```python
    class SentimentAnalysis(BaseModel):
        analysis: str = Field(description="A description of the analysis")
        sentiment: bool = Field(description="True for Happy, False for Sad")
    ```

    **Create the Analysis Function**

    This 'analyze' function takes a string as input and is expected to return a `SentimentAnalysis` object by calling the `chain()` function from the `funcchain` library.

    ```python
    def analyze(text: str) -> SentimentAnalysis:
        """
        Determines the sentiment of the text.
        """
        return chain()
    ```

    **Execution Configuration**

    In the main block, configure the global settings to set the preferred LLM, enable console streaming, and run the `analyze` function with sample text.

    ```python
    settings.llm = "ollama/openchat"
    settings.console_stream = True
    poem = analyze("I really like when my dog does a trick!")
    print(poem)
    ```

    !!!Important
        We need to note here is that `settings.llm` can be adjusted to any model mentioned in [MODELS.md](https://github.com/shroominic/funcchain/blob/main/MODELS.md) and your funcchain code will still work and `chain()` does everything in the background for you.
