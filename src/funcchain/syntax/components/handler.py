from typing import Union

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_core.runnables.history import RunnableWithMessageHistory

from ...backend.settings import settings
from ...model.defaults import univeral_model_selector
from ...utils.msg_tools import msg_to_str

UniversalLLM = Union[BaseChatModel, str, None]


def load_universal_llm(llm: UniversalLLM) -> BaseChatModel:
    if isinstance(llm, str):
        settings.llm = llm
        llm = None
    if not llm:
        llm = univeral_model_selector(settings)
    return llm


# def history_handler(input: Iterator[Any]) -> Iterator[Any]:

#     for chunk in input:
#         yield chunk


def BasicChatHandler(
    *,
    llm: UniversalLLM = None,
    chat_history: BaseChatMessageHistory | None = None,
    system_message: str = "",
) -> Runnable[HumanMessage, AIMessage]:
    if chat_history is None:
        from ...utils.memory import ChatMessageHistory

        chat_history = ChatMessageHistory()

    llm = load_universal_llm(llm)

    handler_chain = (
        ChatPromptTemplate.from_messages(
            [
                *(("system", system_message) if system_message else []),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{user_msg}"),
            ]
        )
        | llm
    )
    return {
        # todo handle images
        "user_msg": lambda x: msg_to_str(x),
    } | RunnableWithMessageHistory(
        handler_chain,  # type: ignore
        get_session_history=lambda _: chat_history,
        input_messages_key="user_msg",
        history_messages_key="history",
    )
