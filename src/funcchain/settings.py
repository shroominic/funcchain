"""
Funcchain Settings:
Automatically loads environment variables from .env file
"""
from typing import Optional, TypedDict

from langchain.cache import InMemoryCache
from langchain.chat_models.base import BaseChatModel
from langchain.globals import set_llm_cache
from langchain.schema.runnable import RunnableWithFallbacks
from pydantic import Field
from pydantic_settings import BaseSettings

set_llm_cache(InMemoryCache())


class FuncchainSettings(BaseSettings):
    debug: bool = True

    llm: BaseChatModel | RunnableWithFallbacks | str = Field(
        default="openai/gpt-3.5-turbo-1106",
        validate_default=False,
    )

    local_models_path: str = "./.models"

    default_system_prompt: str = ""

    retry_parse: int = 5
    retry_parse_sleep: float = 0.1

    # KEYS
    openai_api_key: Optional[str] = None
    azure_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None

    # MODEL KWARGS
    verbose: bool = False
    max_tokens: int = 2048
    temperature: float = 0.1
    context_lenght: int = 8196
    streaming: bool = False

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

    def llama_kwargs(self) -> dict:
        return {
            "n_ctx": self.context_lenght,
        }


settings = FuncchainSettings()


class SettingsOverride(TypedDict, total=False):
    llm: BaseChatModel | RunnableWithFallbacks | str

    verbose: bool
    temperature: float
    max_tokens: int
    streaming: bool
    # TODO: context_length: int


def get_settings(override: Optional[SettingsOverride] = None) -> FuncchainSettings:
    if override:
        return settings.model_copy(update=dict(override))
    return settings
