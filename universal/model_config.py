from typing import Optional, Union, Tuple, Any
from pydantic_settings import BaseSettings


class ChatModelConfig(BaseSettings):
    """
    General Chat Model Configuration and API KEYs
    """
    
    # KEYS
    OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str]  = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    JINACHAT_API_KEY: Optional[str] = None
    
    # KWARGS
    MODEL_NAME: Optional[str] = None
    MODEL_TEMPERATURE: Optional[float] = None
    MODEL_VERBOSE: bool = False
    
    def kwargs(self) -> dict[str, Any]:
        return {
            (k.removeprefix("MODEL_").lower()): v
            for k, v
            in self.model_dump(
                exclude_none=True,
            ).items()
        }