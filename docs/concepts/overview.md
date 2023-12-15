# Concepts

## Concepts Overview

| name | description |
|-|-|
| chain | Main funcchain to get responses from the assistant |
| achain | Async version of chain |
| settings | Global settings object |
| BaseModel | Pydantic model base class |

## chain

The `chain` function is the main interface to get responses from the assistant. It handles creating the prompt, querying the model, and parsing the response.

Key things:

- Takes instruction and system prompt strings to create the prompt
- Automatically extracts docstring of calling function as instruction
- Gets output parser based on return type annotation
- Supports OpenAI Functions under the hood
- Retries on parser failure
- Logs tokens usage

Usage:

```python
from funcchain import chain


def get_weather(city: str) -> str:
    """
    Get the weather for {city}.
    """
    return chain()

print(get_weather("Barcelona"))
```

## achain

The `achain` function is an async version of `chain` that can be awaited.

Usage:

```python
from funcchain import achain
import asyncio


async def get_weather(city: str) -> str:
    """
    Get the weather for {city}.
    """
    return await achain()


print(asyncio.run(get_weather("Barcelona")))
```

## settings

The `settings` object contains global settings for funcchain.

Key attributes:

- `llm`: Configures the default llm
- `max_tokens`: Max tokens per request
- `default_system_prompt`: Default system prompt
- `openai_api_key`: OpenAI API key
- `model_kwargs()`: kwargs for model like temperature

Usage:

```python
from funcchain import settings

settings.llm = MyCustomChatModel()
settings.max_tokens = 2048
```

## BaseModel

`BaseModel` is the Pydantic model base class used to define output schemas.

Funcchain can automatically parse responses to Pydantic models.

Usage:

```python
from funcchain import chain
from pydantic import BaseModel, Field


class Article(BaseModel):
    title: str = Field(description="Title of the article")
    description: str = Field(description="Description of the content of the article")


def summarize(text: str) -> Article:
    """
    Summarize the text into an Article:
    {text}
    """
    return chain()


print(
    summarize(
        """
        AI has the potential to revolutionize education, offering personalized and individualized teaching, and improved learning outcomes. AI can analyze student data and provide real-time feedback to teachers and students, allowing them to adjust their teaching and learning strategies accordingly. One of the biggest benefits of AI in education is the ability to provide personalized and individualized teaching. AI can analyze student data and create a personalized learning plan for each individual student, taking into account their strengths, weaknesses, and learning styles. This approach has the potential to dramatically improve learning outcomes and engagement. The potential of AI in education is enormous, and it is expected to revolutionize the way we approach degree and diploma programs in the future. AI-powered technologies can provide students with real-time feedback, help them to stay on track with their studies, and offer a more personalized and engaging learning experience.
        """
    )
)
```
