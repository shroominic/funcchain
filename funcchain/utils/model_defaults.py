from typing import Type

from dotenv import load_dotenv
from langchain.chat_models import *
from langchain.chat_models.base import BaseChatModel
from langchain.schema.runnable import RunnableWithFallbacks

from funcchain.config import settings


def auto_model(**kwargs) -> Type[BaseChatModel]:
    if settings.AZURE_DEPLOYMENT_NAME_LONG:
        return model_from_env(**kwargs)


def model_from_env(
    dotenv_path: str = "./.env",
    **kwargs,
) -> Type[BaseChatModel]:
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
        "Model not found! "
        "Make sure to use the correct env variables."
        # "For more info: docs.url"
    )


def model_from_name(
    model_name: str,
    /,
    **kwargs,
) -> Type[BaseChatModel]:
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
    kwargs["model_name"] = name

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
        "Model not found! "
        "Make sure to use the correct env variables."
        # "For more info: docs.url"
    )


def create_long_llm() -> RunnableWithFallbacks:
    """
    Create a LLM model with fallbacks for long context.
    Prefer Azure if available.

    Raises:
    - ValueError: If no API key is provided.
    """
    settings.MAX_TOKENS = 8192
    if settings.AZURE_API_KEY:
        config = {
            "openai_api_type": "azure",
            "openai_api_key": settings.AZURE_API_KEY,
            "openai_api_base": settings.AZURE_API_BASE,
            "openai_api_version": settings.AZURE_API_VERSION,
        }
        config.update(settings.model_kwargs())
        print("Model: AZURE")
        return AzureChatOpenAI(
            deployment_name=settings.AZURE_DEPLOYMENT_NAME,
            model_name=config.pop("model_name", "gpt-4"),
            **config,
        ).with_fallbacks(
            [
                AzureChatOpenAI(
                    model_name="gpt-4-32k",
                    deployment_name=settings.AZURE_DEPLOYMENT_NAME_LONG or "gpt-4-32k",
                    **config,
                )
            ]
        )
    if settings.OPENAI_API_KEY:
        config = settings.model_kwargs()
        print("Model: OPENAI")
        return ChatOpenAI(
            model_name=config.pop("model_name", "gpt-3.5-turbo"),
            **config,
        ).with_fallbacks(
            [
                ChatOpenAI(
                    model_name="gpt-4-32k",
                    **config,
                ),
            ]
        )
    raise ValueError("Not OpenAI API key provided.")
