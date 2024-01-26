from pathlib import Path
from typing import Any

from langchain_core.language_models import BaseChatModel

from ..backend.settings import FuncchainSettings
from ..model.patches.llamacpp import ChatLlamaCpp


def get_gguf_model(
    name: str,
    label: str,
    settings: FuncchainSettings,
) -> Path:
    """
    Gather GGUF model from huggingface/TheBloke

    possible input:
    - DiscoLM-mixtral-8x7b-v2-GGUF
    - TheBloke/DiscoLM-mixtral-8x7b-v2
    - discolm-mixtral-8x7b-v2
    ...

    Raises ModelNotFound(name) error in case of no result.
    """
    from huggingface_hub import hf_hub_download

    name = name.removesuffix("-GGUF")
    label = "Q5_K_M" if label == "latest" else label

    model_path = Path(settings.local_models_path)

    if (p := model_path / f"{name.lower()}.{label}.gguf").exists():
        return p

    # check if available on huggingface
    try:
        # check local cache

        input(
            f"Do you want to download this model from huggingface.co/TheBloke/{name}-GGUF ?\n"
            "Press enter to continue."
        )
        print("\033c")
        print("Downloading model from huggingface...")
        p = hf_hub_download(
            repo_id=f"TheBloke/{name}-GGUF",
            filename=f"{name.lower()}.{label}.gguf",
            local_dir=model_path,
            local_dir_use_symlinks=True,
        )
        print("\033c")
        return Path(p)
    except Exception as e:
        print(e)
        raise ValueError(f"ModelNotFound: {name}.{label}")


def default_model_fallback(
    settings: FuncchainSettings,
    **model_kwargs: Any,
) -> ChatLlamaCpp:
    """
    Give user multiple options for local models to download.
    """
    if input("ModelNotFound: Do you want to download a local model instead?").lower().startswith("y"):
        model_kwargs.update(settings.llamacpp_kwargs())
        return ChatLlamaCpp(
            model_path=get_gguf_model("neural-chat-7b-v3-1", "Q4_K_M", settings).as_posix(),
            **model_kwargs,
        )
    print("Please select a model to use funcchain!")
    exit(0)


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
    - "llamacpp/openchat-3.5-0106"  (theblock gguf models)
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
                    from .patches.ollama import ChatOllama

                    model = model_kwargs.pop("model_name")
                    model_kwargs.update(settings.ollama_kwargs())
                    return ChatOllama(model=model, **model_kwargs)

                case "llamacpp" | "thebloke" | "gguf":
                    from .patches.llamacpp import ChatLlamaCpp

                    model_kwargs.pop("model_name")
                    name, label = name.split(":") if ":" in name else (name, "latest")
                    model_path = get_gguf_model(name, label, settings).as_posix()
                    print("Using model:", model_path)
                    model_kwargs.update(settings.llamacpp_kwargs())
                    return ChatLlamaCpp(
                        model_path=model_path,
                        **model_kwargs,
                    )

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
