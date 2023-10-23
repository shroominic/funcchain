# Getting Started

## Welcome

funcchain is the *most pythonic* way of writing cognitive systems. Leveraging pydantic models as output schemas combined with langchain in the backend allows for a seamless integration of llms into your apps.
It works perfect with OpenAI Functions and soon with other models using JSONFormer.

Key features:

- increased productivity
- prompts as Python functions
- pydantic models as output schemas
- langchain schemas in the backend
- fstrings or jinja templates for prompts
- fully utilises OpenAI Functions
- minimalistic and easy to use

## Installation

funcchain requires python 3.10+
```bash
pip install funcchain
```

Make sure to have an OpenAI API key in your environment variables. For example,

```bash
export OPENAI_API_KEY=sk-...
```

## Usage

```python
from funcchain import chain

def hello() -> str:
    """Say hello in 3 languages"""
    return chain()

print(hello())
```

This will call the OpenAI API and return the response.

The `chain` function extracts the docstring as the prompt and the return type for parsing the response.

## Contributing

To contribute, clone the repo and run:

```
./dev_setup.sh
```

This will install pre-commit hooks, dependencies and set up the environment.

To activate the virtual environment managed by poetry, you can use the following command:

```bash
poetry shell
```
