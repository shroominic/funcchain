from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

verified_openai_function_models = [
    "gpt-4",
    "gpt-4o",
    "gpt-4o-2024-05-13",
    "gpt-4-0613",
    "gpt-4-0125-preview",
    "gpt-4-1106-preview",
    "gpt-4-0106-preview",
    "gpt-4-turbo-preview",
    "gpt-4-32k",
    "gpt-4-32k-0613",
    "gpt-4-turbo",
    "gpt-4-turbo-2024-04-09",
    "gpt-4-turbo-preview",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo-1106",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-16k-0613",
]

verified_openai_vision_models = [
    "gpt-4o",
    "gpt-4o-2024-05-13",
    "gpt-4-turbo",
    "gpt-4-turbo-2024-04-09",
    "gpt-4-vision-preview",
]

verified_ollama_vision_models = [
    "llava",
    "bakllava",
]  # TODO: llamacpp


def gather_llm_type(llm: BaseChatModel, func_check: bool = True) -> str:
    from langchain_openai import ChatOpenAI

    if not isinstance(llm, BaseChatModel):
        return "base_model"
    if isinstance(llm, ChatOpenAI):
        if llm.model_name in verified_openai_vision_models:
            return "vision_model"
        if llm.model_name in verified_openai_function_models:
            return "function_model"
        try:
            if func_check:
                llm.invoke(
                    [
                        SystemMessage(content=("This is a test message to see " "if the model can run functions.")),
                        HumanMessage(content="Hello!"),
                    ],
                    functions=[
                        {
                            "name": "print",
                            "description": "show the input",
                            "parameters": {
                                "properties": {
                                    "__arg1": {"title": "__arg1", "type": "string"},
                                },
                                "required": ["__arg1"],
                                "type": "object",
                            },
                        }
                    ],
                )
        except Exception:
            return "chat_model"
        else:
            return "function_model"
    from .patches.ollama import ChatOllama

    if isinstance(llm, ChatOllama):
        for model in verified_ollama_vision_models:
            if llm.model in model:
                return "vision_model"

    from langchain_groq import ChatGroq

    if isinstance(llm, ChatGroq):
        return "json_model"

    return "chat_model"


def is_openai_function_model(
    llm: BaseChatModel,
) -> bool:
    return gather_llm_type(llm) == "function_model"


def is_json_mode_model(
    llm: BaseChatModel,
) -> bool:
    return gather_llm_type(llm, func_check=False) == "json_model"


def is_vision_model(
    llm: BaseChatModel,
) -> bool:
    return gather_llm_type(llm) == "vision_model"
