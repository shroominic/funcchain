from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from ...backend.settings import create_local_settings
from ...model.defaults import univeral_model_selector
from ...schema.types import ChatHandler, OptionalChatHistoryFactory, UniversalChatModel
from ...utils.memory import InMemoryChatMessageHistory, create_history_factory
from ...utils.msg_tools import msg_to_str


def load_universal_llm(llm: UniversalChatModel) -> BaseChatModel:
    if isinstance(llm, str):
        settings = create_local_settings({"llm": llm})
        llm = None
    if not llm:
        llm = univeral_model_selector(settings)
    return llm


def create_chat_handler(
    *,
    llm: UniversalChatModel = None,
    history_factory: OptionalChatHistoryFactory = None,
    system_message: str = "",
) -> ChatHandler:
    history_factory = history_factory or create_history_factory(InMemoryChatMessageHistory)
    llm = load_universal_llm(llm)

    chat_handler_chain = (
        ChatPromptTemplate.from_messages(
            [
                *([("system", system_message)] if system_message else []),  # todo test this
                MessagesPlaceholder(variable_name="history"),
                ("human", "{message}"),
            ]
        )
        | llm
    )
    return {
        # todo handle images
        "message": lambda x: msg_to_str(x),
    } | RunnableWithMessageHistory(
        chat_handler_chain,  # type: ignore
        get_session_history=history_factory,
        input_messages_key="message",
        history_messages_key="history",
    )
