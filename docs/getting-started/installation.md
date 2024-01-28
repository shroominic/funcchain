# Installation

<div class="termy">
```bash
pip install funcchain
```
</div>

For additional features you can also install:

- funcchain  (`langchain_core + openai`)
- funcchain[ollama]  (you need to install this [ollama fork]() for grammar support)
- funcchain[llamacpp]  (using `llama-cpp-python`)
- funcchain[pillow]  (for vision model features)
- funcchain[all]  (includes everything)

To enter this in your terminal you need to write it like this:
`pip install "funcchain[all]"`

## Environment

Make sure to have an OpenAI API key in your environment variables. For example,

```bash
export OPENAI_API_KEY=sk-**********
```

But you can also create a `.env` file in your current working directory and include the key there.
The dot env file will load automatically.
