# Funcchain Configuration

## Set Global Settings

In every project you use funcchain in you can specify global settings. This is done by importing the `settings` object from the `funcchain` package.

```python
from funcchain import settings
```

You can then change the settings like here:

```python
settings.llm = "openai/gpt-4-vision-preview"
```

## Set Local Settings

If you want to set local settings only applied to a specific funcchain function you
can set them using the SettingsOverride class.

```python
from funcchain import chain
from funcchain.settings import SettingsOverride

def analyse_output(
    goal: str
    output: str,
    settings: SettingsOverride = {},
) -> OutputAnalysis:
    """
    Analyse the output and determine if the goal is reached.
    """
    return chain(settings_override=settings)

result = analyse_output(
    "healthy outpout",
    "Hello World!",
    settings={"llm": "openai/gpt-4-vision-preview"},
)
```

The `settings_override` argument is a `SettingsOverride` object which is a dict-like object that can be used to override the global settings.
You will get suggestions from your IDE on what settings you can override due to the type hints.

## Settings Class Overview

The configuration settings for Funcchain are encapsulated within the `FuncchainSettings` class. This class inherits from Pydantic's `BaseSettings`.

`funcchain/backend/settings.py`

```python
class FuncchainSettings(BaseSettings):
    ...
```

## Setting Descriptions

### General Settings

- `debug: bool = True`
  Enables or disables debug mode.

- `llm: BaseChatModel | str = "openai/gpt-3.5-turbo-1106"`
  Defines the language learning model to be used. It can be a type of `BaseChatModel` or `str` (model_name).
  Checkout the [MODELS.md](https://github.com/shroominic/funcchain/blob/main/MODELS.md) file for a list and schema of supported models.

- `console_stream: bool = False`
  Enables or disables token streaming to the console.

- `system_prompt: str = ""`
  System prompt used as first message in the chat to instruct the model.

- `retry_parse: int = 3`
  Number of retries for auto fixing pydantic validation errors.

- `retry_parse_sleep: float = 0.1`
  Sleep time between retries.

### Model Keyword Arguments

- `verbose: bool = False`
  Enables or disables verbose logging for the model.

- `streaming: bool = False`
  Enables or disables streaming for the model.

- `max_tokens: int = 2048`
  Specifies the maximum number of output tokens for chat models.

- `temperature: float = 0.1`
  Controls the randomness in the model's output.

### LlamaCPP Keyword Arguments

- `context_lenght: int = 8196`
  Specifies the context length for the LlamaCPP model.

- `n_gpu_layers: int = 42`
  Specifies the number of GPU layers for the LlamaCPP model.
  Choose 0 for CPU only.

- `keep_loaded: bool = False`
  Determines whether to keep the LlamaCPP model loaded in memory.

- `local_models_path: str = "./.models"`
  Specifies the local path for storing models.
