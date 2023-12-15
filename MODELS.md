# Supported Models

## LangChain Chat Models

You can set the `settings.llm` with any ChatModel the LangChain library.

```python
from langchain.chat_models import AzureChatOpenAI

settings.llm = AzureChatOpenAI(...)
```

## String Model Identifiers

You can also set the `settings.llm` with a string identifier of a ChatModel including local models.

### Schema

`<provider>/<name>:<optional_label>`

### Providers

- `openai`: OpenAI Chat Models
- `gguf`: Huggingface GGUF Models from TheBloke using LlamaCpp
- `local` | `thebloke` | `huggingface`: alias for `gguf`

### Examples

- `openai/gpt-3.5-turbo`: Classic ChatGPT
- `gguf/deepseek-llm-7b-chat`: DeepSeek LLM 7B Chat
- `gguf/OpenHermes-2.5-7B`: OpenHermes 2.5
- `TheBloke/deepseek-llm-7B-chat-GGUF:Q3_K_M`: (eg thebloke huggingface identifier)
- `local/neural-chat-7B-v3-1`: Neural Chat 7B (local as alias for gguf)

### additional notes

Checkout the file `src/funcchain/utils/model_defaults.py` for the code that parses the string identifier.
Feel free to create a PR to add more models to the defaults. Or tell me how wrong I am and create a better system.
