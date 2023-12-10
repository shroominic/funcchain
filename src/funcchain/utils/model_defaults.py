from typing import Any

from dotenv import load_dotenv
from langchain.chat_models import (
    AzureChatOpenAI,
    ChatAnthropic,
    ChatGooglePalm,
    ChatOpenAI,
)
from langchain.chat_models.base import BaseChatModel

from ..settings import settings


class ModelNotFoundError(LookupError):
    ...


class MissingApiKeyError(ValueError):
    ...


def model_from_env(
    dotenv_path: str = "./.env",
    **kwargs: Any,
) -> BaseChatModel | None:
    """
    Automatically search your env variables for api keys
    and gives you the corresponding chat model interface.

    Supporting:
    - OPENAI_API_KEY
    - AZURE_API_KEY
    - ANTHROPIC_API_KEY
    - GOOGLE_API_KEY

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
    return None


def get_gguf_model(name: str, label: str) -> str:
    """
    Gather GGUF model from huggingface/TheBloke
    e.g. https://huggingface.co/TheBloke/OpenHermes-2.5-neural-chat-7B-v3-1-7B-GGUF

    Raises ModelNotFound(model_name) error in case of no result.
    """
    # check if model already downloaded
    # if so return None

    # check if available on huggingface
    # if not raise

    # ask before downloading
    # if not suggest other options

    # download to settings.MODEL_LIBRARY_PATH

    return f"{settings.MODEL_LIBRARY}/{name}_{label}.gguf"


def univeral_model_selector(
    model_name: str | None,
    **model_kwargs: Any,
) -> BaseChatModel:
    """
    Automatically selects the best possible model for a given ModelName.
    You can use this schema:

    "provider/model_name:"

    and automatically select the right model for you.
    You can add optional model kwargs like temperature.

    Examples:
    - "openai/gpt-3.5-turbo"
    - "anthropic/claude-2"
    - "llamacpp/neural-chat:7b-v3.1-q8_0"


    Supported:
        [ openai, anthropic, google, llamacpp ]

    Raises:
    - ModelNotFoundError, when the model is not found.
    """
    if not model_name:
        if model := model_from_env(**model_kwargs):
            return model
        raise ModelNotFoundError(
            "Please specify a model_name or add certain env variables."
            "You can checkout out docs for supported models: todowritedocs.com"
        )

    mtype, name_lable = model_name.split("/")
    name, label = name_lable.split(":")

    model_kwargs["model_name"] = name

    if mtype:
        match type:
            case "openai":
                return ChatOpenAI(**model_kwargs)
            case "anthropic":
                return ChatAnthropic(**model_kwargs)
            case "google":
                return ChatGooglePalm(**model_kwargs)
            case "llamacpp":
                return ChatLlamaCpp(
                    model_path=get_gguf_model(name, label),
                    **model_kwargs,
                )
