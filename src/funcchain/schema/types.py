from typing import Callable, Optional, Union

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable

UniversalChatModel = Union[BaseChatModel, str, None]

ChatHandler = Runnable[HumanMessage, AIMessage]

ChatHistoryFactory = Callable[..., BaseChatMessageHistory]

OptionalChatHistoryFactory = Optional[ChatHistoryFactory]
