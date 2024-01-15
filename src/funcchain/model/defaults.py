from typing import Any

from langchain_core.language_models import BaseChatModel

from ..backend.settings import FuncchainSettings


def univeral_model_selector(
    settings: FuncchainSettings,
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
    - "ollama/deepseek-llm-7b-chat"

    Supported:
        [ openai, anthropic, google, ollama ]

    Raises:
    - ModelNotFoundError, when the model is not found.
    """
    model_name = settings.llm if isinstance(settings.llm, str) else ""
    model_kwargs.update(settings.model_kwargs())

    if model_name:
        mtype, name = model_name.split("/") if "/" in model_name else ("", model_name)
        mtype = mtype.lower()

        model_kwargs["model_name"] = name

        try:
            match mtype:
                case "openai":
                    from langchain_openai.chat_models import ChatOpenAI

                    model_kwargs.update(settings.openai_kwargs())
                    return ChatOpenAI(**model_kwargs)

                case "anthropic":
                    from langchain_community.chat_models import ChatAnthropic

                    return ChatAnthropic(**model_kwargs)

                case "google":
                    from langchain_community.chat_models import ChatGooglePalm

                    return ChatGooglePalm(**model_kwargs)

                case "ollama":
                    from .llm_overrides import ChatOllama

                    model = model_kwargs.pop("model_name")
                    model_kwargs.update(settings.ollama_kwargs())
                    return ChatOllama(model=model, **model_kwargs)

        except Exception as e:
            print("ERROR:", e)
            raise e

        try:
            if "gpt-4" in name or "gpt-3.5" in name:
                from langchain_openai.chat_models import ChatOpenAI

                model_kwargs.update(settings.openai_kwargs())
                return ChatOpenAI(**model_kwargs)

        except Exception as e:
            print(e)

    model_kwargs.pop("model_name")

    if settings.openai_api_key:
        from langchain_openai.chat_models import ChatOpenAI

        model_kwargs.update(settings.openai_kwargs())
        return ChatOpenAI(**model_kwargs)

    if settings.azure_api_key:
        from langchain_openai.chat_models import AzureChatOpenAI

        return AzureChatOpenAI(**model_kwargs)

    if settings.anthropic_api_key:
        from langchain_community.chat_models import ChatAnthropic

        return ChatAnthropic(**model_kwargs)

    if settings.google_api_key:
        from langchain_community.chat_models import ChatGooglePalm

        return ChatGooglePalm(**model_kwargs)

    raise ValueError(
        "Could not read llm selector string. Please check "
        "[here](https://github.com/shroominic/funcchain/blob/main/MODELS.md) "
        "for more info."
    )
