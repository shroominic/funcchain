<!-- markdownlint-disable MD033 MD046 -->
# Image Analysis with Funcchain and Pydantic

!!! Example
    [vision.py](https://github.com/shroominic/funcchain/blob/main/examples/vision.py)

    This is a useful task for applications that need to extract structured information from images.
    You can adapt this for your own usage.
    This serves as an example of how to implement image analysis using the funcchain library's integration with openai/gpt-4-vision-preview.

## Full Code Example

<pre><code id="codeblock">
```python
from funcchain import Image, chain, settings
from pydantic import BaseModel, Field

settings.llm = "openai/gpt-4-vision-preview"
# settings.llm = "ollama/bakllava"
settings.console_stream = True

class AnalysisResult(BaseModel):
    """The result of an image analysis."""

    theme: str = Field(description="The theme of the image")
    description: str = Field(description="A description of the image")
    objects: list[str] = Field(description="A list of objects found in the image")

def analyse_image(image: Image) -> AnalysisResult:
    """
    Analyse the image and extract its
    theme, description and objects.
    """
    return chain()

if __name__ == "__main__":
    example_image = Image.from_file("examples/assets/old_chinese_temple.jpg")

    result = analyse_image(example_image)

    print("Theme:", result.theme)
    print("Description:", result.description)
    for obj in result.objects:
        print("Found this object:", obj)
```
</code></pre>

Demo

<div class="termy">
```python
Theme: Ancient Architecture
Description: An old Chinese temple with intricate designs.
Found this object: temple
Found this object: tree
Found this object: sky
```
</div>

## Instructions

!!! Step-by-Step
    Oiur goal is the functionality is to analyze an image and extract its theme, a description, and a list of objects found within it.

    **Necessary Imports**
    ```python
    from funcchain import Image, chain, settings
    from pydantic import BaseModel, Field
    ```

    **Configure Settings**
    The settings are configured to use a specific language model capable of image analysis and to enable console streaming for immediate output.
    ```python
    settings.llm = "openai/gpt-4-vision-preview"
    settings.console_stream = True
    ```

    **Define the AnalysisResult Model**
    The AnalysisResult class models the expected output of the image analysis, including the theme, description, and objects detected in the image.

    ```python
    class AnalysisResult(BaseModel):
        theme: str = Field(description="The theme of the image")
        description: str = Field(description="A description of the image")
        objects: list[str] = Field(description="A list of objects found in the image")
    ```

    **Implement the Image Analysis Function**
    The analyse_image function is designed to take an Image object and use the chain function to process the image and return an AnalysisResult object for later usage (here printing).

    ```python
    def analyse_image(image: Image) -> AnalysisResult:
        return chain()
    ```

    **Execute the Analysis**
    This block runs the image analysis on an example image and prints the results when the script is executed directly.

    ```python
    if __name__ == "__main__":
        example_image = Image.from_file("examples/assets/old_chinese_temple.jpg")
        result = analyse_image(example_image)
        print("Theme:", result.theme)
        print("Description:", result.description)
        for obj in result.objects:
            print("Found this object:", obj)
    ```
