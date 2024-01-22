# Supported Models

## LangChain Chat Models

You can set the `settings.llm` with any ChatModel the LangChain library.

```python
from langchain_openai.chat_models import AzureChatOpenAI

settings.llm = AzureChatOpenAI(...)
```

## String Model Identifiers

You can also set the `settings.llm` with a string identifier of a ChatModel including local models.

### Schema

`<provider>/<name>:<optional_label>`

### Providers

- `openai`: OpenAI Chat Models
- `ollama`: Run local models through Ollama(llamacpp)

### Examples

- `openai/gpt-3.5-turbo`: Classic ChatGPT
- `openai/gpt-4-1106-preview`: GPT-4-Turbo
- `ollama/openchat-3.5-
- `ollama/openchat`: OpenChat3.5-1210
- `ollama/openhermes2.5-mistral`: OpenHermes 2.5

### additional notes

Checkout the file `src/funcchain/utils/model_defaults.py` for the code that parses the string identifier.
Feel free to create a PR to add more models to the defaults. Or tell me how wrong I am and create a better system.
