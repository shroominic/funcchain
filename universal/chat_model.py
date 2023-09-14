from typing import Type
from dotenv import load_dotenv
from langchain.chat_models.base import BaseChatModel
from langchain.chat_models import *

from universal.model_config import ChatModelConfig


def model_from_env(
    dotenv_path: str = "./.env",
    **kwargs
) -> Type[BaseChatModel]:
    """
    Automatically search your env variables for api keys
    and gives you the corresponding chat model interface.
    
    Supporting:
    - OPENAI_API_KEY
    - AZURE_OPENAI_API_KEY
    - ANTHROPIC_API_KEY
    - GOOGLE_API_KEY
    - JINACHAT_API_KEY
    
    Raises: 
    - ValueError, when the model is not found.
    """
    load_dotenv(dotenv_path=dotenv_path)
    config = ChatModelConfig()
    kwargs.update(config.kwargs())
    
    if config.OPENAI_API_KEY:
        return ChatOpenAI(**kwargs)
    if config.AZURE_OPENAI_API_KEY:
        return AzureChatOpenAI(**kwargs)
    if config.ANTHROPIC_API_KEY:
        return ChatAnthropic(**kwargs)
    if config.GOOGLE_API_KEY:
        return ChatGooglePalm(**kwargs)
    if config.JINACHAT_API_KEY:
        return JinaChat(**kwargs)
    if name := config.MODEL_NAME:
        return model_from_name(name, **kwargs)
    raise ValueError(
        "Model not found! "
        "Make sure to use the correct env variables."
        # "For more info: docs.url"
    )


def model_from_name(
    model_name: str,
    /,
    **kwargs
) -> Type[BaseChatModel]:
    """ 
    Input model_name using this schema
    
    "provider::model_name"
    
    and automatically select the right model for you.
    You can add optional model kwargs like temperature.
    
    Examples:
    - "openai::gpt-3.5-turbo"
    - "anthropic::claude-2"
    
    Supported: 
        [ openai, anthropic, google, jina ]
    
    Coming Soon: 
        [ local, open_router ]
    
    Raises: 
    - ValueError, when the model is not found.
    """
    type, name = model_name.split("::")
    kwargs["model_name"] = name
    
    match type:
        case "openai":
            return ChatOpenAI(**kwargs)
        case "anthropic":
            return ChatAnthropic(**kwargs)
        case "google":
            return ChatGooglePalm(**kwargs)


__todo__ = [
    "FakeListChatModel",
    "PromptLayerChatOpenAI",
    "ChatMLflowAIGateway",
    "ChatOllama",
    "ChatVertexAI",
    "HumanInputChatModel",
    "ChatAnyscale",
    "ChatLiteLLM",
    "ErnieBotChat",
]