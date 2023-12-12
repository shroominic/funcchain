"""
Funcchain Settings:
Automatically loads environment variables from .env file
"""
from typing import Optional, TypedDict

from dotenv import load_dotenv
from langchain.cache import InMemoryCache
from langchain.chat_models.base import BaseChatModel
from langchain.globals import set_llm_cache
from langchain.schema.runnable import RunnableWithFallbacks
from pydantic_settings import BaseSettings

load_dotenv("./.env")

set_llm_cache(InMemoryCache())


class FuncchainSettings(BaseSettings):
    # General
    LLM: BaseChatModel | RunnableWithFallbacks | None = None
    DEBUG: bool = True

    # TODO: merge LLM and MODEL_NAME
    MODEL_NAME: str = "openai/gpt-3.5-turbo-1106"
    MODEL_LIBRARY: str = "./.models"

    # Prompt
    DEFAULT_SYSTEM_PROMPT: str = ""

    RETRY_PARSE: int = 5
    RETRY_PARSE_SLEEP: float = 0.1

    # KEYS
    OPENAI_API_KEY: Optional[str] = None
    AZURE_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None

    # MODEL KWARGS
    VERBOSE: bool = False
    MAX_TOKENS: int = 2048
    TEMPERATURE: float = 0.1
    CONTEXT_LENGTH: int = 8196
    STREAMING: bool = False

    def model_kwargs(self) -> dict:
        return {
            "verbose": self.VERBOSE,
            "temperature": self.TEMPERATURE,
            "max_tokens": self.MAX_TOKENS,
            "streaming": self.STREAMING,
        }

    def openai_kwargs(self) -> dict:
        return {
            "openai_api_key": self.OPENAI_API_KEY,
        }

    def llama_kwargs(self) -> dict:
        return {
            "n_ctx": self.CONTEXT_LENGTH,
        }


settings = FuncchainSettings()


class SettingsOverride(TypedDict, total=False):
    llm: BaseChatModel | RunnableWithFallbacks | None
    model_name: str

    verbose: bool
    temperature: float
    max_tokens: int
    streaming: bool
    # context_length: int


def get_settings(override: Optional[SettingsOverride] = None) -> FuncchainSettings:
    if override:
        return settings.model_copy(update=dict(override))
    return settings
