<!-- markdownlint-disable MD033 MD046 -->
# Installation

<div class="termy">

```bash
$ pip install funcchain
---> 100%
```

</div>

For additional features you can also install:

- `funcchain` (langchain_core + openai)
- `funcchain[ollama]` (you need to install this [ollama fork](https://github.com/ollama/ollama/pull/1606) for grammar support)
- `funcchain[llamacpp]` (using llama-cpp-python)
- `funcchain[pillow]` (for vision model features)
- `funcchain[all]` (includes everything)

To enter this in your terminal you need to write it like this:
`pip install "funcchain[all]"`

## Environment

Make sure to have an OpenAI API key in your environment variables. For example,

<div class="termy">

```bash
export OPENAI_API_KEY="sk-rnUPxirSQ4bmz2He4qyaiKShdXJcsOsTg"
```

</div>

But you can also create a `.env` file in your current working directory and include the key there.
The dot env file will load automatically.
