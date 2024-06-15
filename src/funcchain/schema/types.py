from typing import Callable, Union

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.runnables import Runnable

UniversalChatModel = Union[BaseChatModel, str, None]

ChatRunnable = Runnable[list[BaseMessage], AIMessage]

ChatHistoryFactory = Callable[..., BaseChatMessageHistory]
