"""
Funcchain Settings:
Automatically loads environment variables from .env file
"""
from typing import Optional, Any

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv("./.env")


class FuncchainSettings(BaseSettings):
    # General    
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
    MODEL_NAME: Optional[str] = None
    MODEL_TEMPERATURE: float = 0.1
    MODEL_REQUEST_TIMEOUT: float = 210
    MODEL_VERBOSE: bool = False

    def model_kwargs(self) -> dict[str, Any]:
        return {
            "temperature": settings.MODEL_TEMPERATURE,
            "request_timeout": settings.MODEL_REQUEST_TIMEOUT,
            "verbose": settings.VERBOSE,
        }


settings = FuncchainSettings()
