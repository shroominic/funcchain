from typing import Any

from dotenv import load_dotenv
from langchain.chat_models import (
    AzureChatOpenAI,
    ChatAnthropic,
    ChatGooglePalm,
    ChatOpenAI,
    JinaChat,
)
from langchain.chat_models.base import BaseChatModel

from ..settings import settings


def model_from_env(
    dotenv_path: str = "./.env",
    **kwargs: Any,
) -> BaseChatModel:
    """
    Automatically search your env variables for api keys
    and gives you the corresponding chat model interface.

    Supporting:
    - OPENAI_API_KEY
    - AZURE_API_KEY
    - ANTHROPIC_API_KEY
    - GOOGLE_API_KEY
    - JINACHAT_API_KEY

    Raises:
    - ValueError, when the model is not found.
    """
    load_dotenv(dotenv_path=dotenv_path)
    kwargs.update(settings.model_kwargs())

    if settings.OPENAI_API_KEY:
        return ChatOpenAI(**kwargs)
    if settings.AZURE_API_KEY:
        return AzureChatOpenAI(**kwargs)
    if settings.ANTHROPIC_API_KEY:
        return ChatAnthropic(**kwargs)
    if settings.GOOGLE_API_KEY:
        return ChatGooglePalm(**kwargs)
    if settings.JINACHAT_API_KEY:
        return JinaChat(**kwargs)
    if name := settings.MODEL_NAME:
        return model_from_name(name, **kwargs)
    raise ValueError(
        "Model not found! Make sure to use the correct env variables."
        # "For more info: docs.url"
    )


def model_from_name(
    model_name: str,
    /,
    **kwargs: Any,
) -> BaseChatModel:
    """
    Input model_name using this schema

    "provider::model_name"

    and automatically select the right model for you.
    You can add optional model kwargs like temperature.

    Examples:
    - "openai::gpt-3.5-turbo"
    - "anthropic::claude-2"

    Supported:
        [ openai, anthropic, google, jina ]

    Coming Soon:
        [ local, open_router ]

    Raises:
    - ValueError, when the model is not found.
    """
    type, name = model_name.split("::")
    kwargs["model"] = name

    match type:
        case "openai":
            return ChatOpenAI(**kwargs)
        case "azure":
            return AzureChatOpenAI(**kwargs)
        case "anthropic":
            return ChatAnthropic(**kwargs)
        case "google":
            return ChatGooglePalm(**kwargs)
    raise ValueError(
        "Model not found! Make sure to use the correct env variables."
        # "For more info: docs.url"
    )
