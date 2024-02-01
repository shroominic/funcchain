<!-- markdownlint-disable MD033 MD046 -->
# Streaming with Funcchain

!!! Example
    See [stream.py](https://github.com/shroominic/funcchain/blob/main/examples/stream.py)

    This serves as an example of how to implement streaming output for text generation tasks using funcchain.

## Full Code Example

<pre><code id="codeblock">
```python
from funcchain import chain, settings
from funcchain.backend.streaming import stream_to

settings.temperature = 1

def generate_story_of(topic: str) -> str:
    """
    Write a short story based on the topic.
    """
    return chain()

with stream_to(print):
    generate_story_of("a space cat")
```
</code></pre>

Demo

<div class="termy">
    ```python
    with stream_to(print):
        generate_story_of("a space cat")

    $ Once upon a time in a galaxy far, far away, there was a space cat named Whiskertron...
    ```
</div>

## Instructions

!!! Step-by-Step

    **Necessary Imports**

    ```python
    from funcchain import chain, settings
    from funcchain.backend.streaming import stream_to
    ```

    **Configure Settings**

    The settings are configured to set the temperature, which controls the creativity of the language model's output.
    Experiment with different values.

    ```python
    settings.temperature = 1
    ```

    **Define the Story Generation Function**

    The generate_story_of function is designed to take a topic and use the chain function to generate a story.

    ```python
    def generate_story_of(topic: str) -> str:
        """
        Write a short story based on the topic.
        """
        return chain()
    ```

    **Execute the Streaming Generation**

    This block uses the stream_to context manager to print the output of the story generation function as it is being streamed.
    This is how you stream the story while it is being generated.

    ```python
    with stream_to(print):
        generate_story_of("a space cat")
    ```
