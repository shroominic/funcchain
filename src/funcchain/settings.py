"""
Funcchain Settings:
Automatically loads environment variables from .env file
"""
from typing import Any, Optional

from dotenv import load_dotenv
from langchain.chat_models.base import BaseChatModel
from langchain.schema.runnable import RunnableWithFallbacks
from langchain.globals import set_llm_cache
from langchain.cache import InMemoryCache
from pydantic_settings import BaseSettings

load_dotenv("./.env")

set_llm_cache(InMemoryCache())


class FuncchainSettings(BaseSettings):
    # General
    LLM: BaseChatModel | RunnableWithFallbacks | None = None
    DEBUG: bool = True

    RETRY_PARSE: int = 5
    RETRY_PARSE_SLEEP: float = 0.1

    # Prompt
    MAX_TOKENS: int = 4096
    DEFAULT_SYSTEM_PROMPT: str = ""

    # KEYS
    OPENAI_API_KEY: Optional[str] = None
    AZURE_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    JINACHAT_API_KEY: Optional[str] = None

    # KWARGS
    STREAMING: bool = False
    MODEL_NAME: str = "openai::gpt-3.5-turbo-1106"
    MODEL_TEMPERATURE: float = 0.1
    MODEL_REQUEST_TIMEOUT: float = 210
    MODEL_VERBOSE: bool = False

    def model_kwargs(self) -> dict[str, Any]:
        return {
            "model_name": self.MODEL_NAME
            if "::" not in self.MODEL_NAME
            else self.MODEL_NAME.split("::")[1],
            "temperature": self.MODEL_TEMPERATURE,
            "verbose": self.DEBUG,
            "openai_api_key": self.OPENAI_API_KEY,
            "max_tokens": self.MAX_TOKENS,
            "streaming": self.STREAMING,
            # "format": "json",
        }


settings = FuncchainSettings()
