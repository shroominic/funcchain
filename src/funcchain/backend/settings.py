"""
Funcchain Settings:
Automatically loads environment variables from .env file
"""
from typing import Optional

from langchain_core.language_models import BaseChatModel
from pydantic import Field
from pydantic_settings import BaseSettings
from typing_extensions import TypedDict

from ..schema.types import UniversalChatModel


class FuncchainSettings(BaseSettings):
    debug: bool = True

    llm: BaseChatModel | str = Field(
        default="openai/gpt-3.5-turbo",
        validate_default=False,
    )

    console_stream: bool = False

    system_prompt: str = ""

    retry_parse: int = 3
    retry_parse_sleep: float = 0.1

    # LANGSMITH
    # langchain_project: str = "funcchain"
    # langchain_tracing_v2: str = "true"
    # langchain_api_key: str = ""
    # # todo: make langsmith load from here and not the .env

    # PROVIDERS
    openai_api_key: Optional[str] = None
    azure_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"

    # MODEL KWARGS
    verbose: bool = False
    streaming: bool = False
    max_tokens: int = 2048
    temperature: float = 0.1

    # LLAMACPP KWARGS
    context_lenght: int = 8196
    n_gpu_layers: int = 50
    keep_loaded: bool = False
    repeat_penalty: float = 1.0
    local_models_path: str = "./.models"

    def model_kwargs(self) -> dict:
        return {
            "verbose": self.verbose,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "streaming": self.streaming,
        }

    def openai_kwargs(self) -> dict:
        return {
            "openai_api_key": self.openai_api_key,
        }

    def ollama_kwargs(self) -> dict:
        return {
            "base_url": self.ollama_base_url,
        }

    def llamacpp_kwargs(self) -> dict:
        return {
            "n_ctx": self.context_lenght,
            "use_mlock": self.keep_loaded,
            "n_gpu_layers": self.n_gpu_layers,
            "repeat_penalty": self.repeat_penalty,
        }

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = FuncchainSettings()


class SettingsOverride(TypedDict, total=False):
    llm: UniversalChatModel

    verbose: bool
    temperature: float
    max_tokens: int
    streaming: bool
    retry_parse: int
    context_lenght: int
    system_prompt: str


def create_local_settings(override: Optional[SettingsOverride] = None) -> FuncchainSettings:
    if override:
        if override["llm"] is None:
            override["llm"] = settings.llm
        return settings.model_copy(update=dict(override))
    return settings


# load langsmith logging vars
try:
    import dotenv
except ImportError:
    pass
else:
    dotenv.load_dotenv()
