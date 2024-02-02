# Vision Models

Funcchain supports working with vision models so you can use images as input arguments of your prompts.
This only works if you also choose the correct model.
Currently known supported models:

- `openai/gpt-4-vision-preview`
- `ollama/llava` or `ollama/bakllava`

You need to set these using `settings.llm` (checkout the [Funcchain Settings](../getting-started/config.md)).

## Image Type

`from funcchain import Image`

Funcchain introuces a special type for Images to quickly recognise image arguments and format them correctly into the prompt.
This type also exposes a variaty of classmethods for creating but also methods for converting Image instances.

Checkout the [Vision Example](../features/vision.md) for more details.
