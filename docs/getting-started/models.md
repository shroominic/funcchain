# Supported Models

## LangChain Chat Models

You can set the `settings.llm` with any LangChain ChatModel.

```python
from funcchain import settings
from langchain_community.chat_models import AzureChatOpenAI

settings.llm = AzureChatOpenAI(...)
```

## String Model Identifiers

You can also set the `settings.llm` with a string identifier of a ChatModel including local models.

```python
from funcchain import settings

settings.llm = "llamacpp/openchat-3.5-1210"

# ...
```

### Schema

`<provider>/<model_name>:<optional_label>`

### Providers

- `openai`: OpenAI Chat Models
- `llamacpp`: Run local models directly using llamacpp (alias: `thebloke`, `gguf`)
- `ollama`: Run local models through Ollama (wrapper for llamacpp)
- `azure`: Azure Chat Models
- `anthropic`: Anthropic Chat Models
- `google`: Google Chat Models

### Examples

- `openai/gpt-3.5-turbo`: ChatGPT Classic
- `openai/gpt-4-1106-preview`: GPT-4-Turbo
- `ollama/openchat`: OpenChat3.5-1210
- `ollama/openhermes2.5-mistral`: OpenHermes 2.5
- `llamacpp/openchat-3.5-1210`: OpenChat3.5-1210
- `TheBloke/Nous-Hermes-2-SOLAR-10.7B-GGUF`: alias for `llamacpp/...`
- `TheBloke/openchat-3.5-0106-GGUF:Q3_K_L`: with Q label

### additional notes

Checkout the file `src/funcchain/model/defaults.py` for the code that parses the string identifier.
Feel free to create a PR to add more models to the defaults. Or tell me how wrong I am and create a better system.
