from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from ...backend.settings import create_local_settings
from ...model.defaults import univeral_model_selector
from ...schema.types import ChatRunnable, UniversalChatModel


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
    system_message: str | None,
    tools: list[str] = [],
    vision: bool = False,
    read_files: bool = False,
    read_links: bool = False,
    code_interpreter: bool = False,
    **kwargs: Any,
) -> ChatRunnable:
    return (
        {"messages": lambda x: x}
        | ChatPromptTemplate.from_messages(
            [
                *([("system", system_message)] if system_message else []),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        | load_universal_llm(llm)  # type: ignore
    )
