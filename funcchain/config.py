"""
Funcchain Settings:
Automatically loads environment variables from .env file
"""
from typing import Optional, Any

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from langchain.chat_models.base import BaseChatModel
from langchain.schema.runnable import RunnableWithFallbacks


load_dotenv("./.env")


class FuncchainSettings(BaseSettings):
    # General
    LLM: BaseChatModel | RunnableWithFallbacks | None = None
    VERBOSE: bool = True

    # Prompt
    MAX_TOKENS: int = 4096
    DEFAULT_SYSTEM_PROMPT: str = (
        "You are a professional assistant solving tasks for entrepreneurs. "
        "You are very good and passionate about your job!"
    )

    # KEYS
    OPENAI_API_KEY: Optional[str] = None
    AZURE_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    JINACHAT_API_KEY: Optional[str] = None

    # AZURE
    AZURE_API_BASE: Optional[str] = None
    AZURE_DEPLOYMENT_NAME: str = "gpt-4"
    AZURE_DEPLOYMENT_NAME_LONG: Optional[str] = None
    AZURE_API_VERSION: str = "2023-07-01-preview"

    # KWARGS
    MODEL_NAME: str = "openai::gpt-3.5-turbo"
    MODEL_TEMPERATURE: float = 0.1
    MODEL_REQUEST_TIMEOUT: float = 210
    MODEL_VERBOSE: bool = False

    def model_kwargs(self) -> dict[str, Any]:
        return {
            "model_name": self.MODEL_NAME
            if "::" not in self.MODEL_NAME
            else self.MODEL_NAME.split("::")[1],
            "temperature": self.MODEL_TEMPERATURE,
            "request_timeout": self.MODEL_REQUEST_TIMEOUT,
            "verbose": self.VERBOSE,
        }


settings = FuncchainSettings()
