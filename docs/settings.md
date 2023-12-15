# Settings

## Settings Class Overview

The configuration settings for Funcchain are encapsulated within the `FuncchainSettings` class. This class inherits from Pydantic's `BaseSettings`.

`funcchain/config.py`

```python
class FuncchainSettings(BaseSettings):
    ...
```

## Setting Descriptions

### General Settings

- `llm: BaseChatModel | RunnableWithFallbacks | str = "openai/gpt-3.5-turbo"`
  Defines the language learning model to be used. It can be a type of `BaseChatModel`, `RunnableWithFallbacks`, or `str` (model_name).

- `verbose: bool = True`
  Enables or disables verbose logging.

### Prompt Settings

- `max_tokens: int = 4096`
  Specifies the maximum number of tokens for chat models.

- `default_system_prompt: str = "You are a professional assistant solving tasks."`
  Default prompt used for initializing the system.

### API Keys

- `openai_api_key: Optional[str] = None`
  API key for the OpenAI service.

- `azure_api_key: Optional[str] = None`
  API key for the Azure service.

- `anthropic_api_key: Optional[str] = None`
  API key for the Anthropic service.

- `google_api_key: Optional[str] = None`
  API key for the Google service.

- `JINACHAT_API_KEY: Optional[str] = None`
  API key for the JinaChat service.

### Azure Settings

- `AZURE_API_BASE: Optional[str] = None`
  Base URL for the Azure API.

- `AZURE_DEPLOYMENT_NAME: str = "gpt-4"`
  Deployment name for the Azure service.

- `AZURE_DEPLOYMENT_NAME_LONG: Optional[str] = None`
  Extended deployment name for the Azure service, if applicable.

- `AZURE_API_VERSION: str = "2023-07-01-preview"`
  API version for the Azure service.

### Model Keyword Arguments

- `temperature: float = 0.1`
  Controls the randomness in the model's output.

- `verbose: bool = False`
  Enables or disables verbose logging for the model.

### Additional Methods

- `model_kwargs(self) -> dict[str, Any]`
  Method that returns a dictionary of keyword arguments for the model initialization based on the settings.
