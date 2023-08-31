"""
Funcchain Settings:
Automatically loads environment variables from .env file
"""
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv("./.env")


class FuncchainSettings(BaseSettings):
    # General
    DEBUG: bool = False

    # Prompt
    MAX_TOKENS: int = 4096
    DEFAULT_SYSTEM_PROMPT: str = (
        "You are a professional assistant solving tasks for entrepreneurs. "
        "You are very good and passionate about your job!"
    )

    # Model
    OPENAI_API_KEY: str = ""
    AZURE_API_KEY: str = ""
    AZURE_API_BASE: str = ""
    AZURE_DEPLOYMENT_NAME: str = ""
    AZURE_API_VERSION: str = ""


settings = FuncchainSettings()
