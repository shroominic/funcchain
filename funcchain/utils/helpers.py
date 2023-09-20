import asyncio
from functools import wraps
from typing import NoReturn, Type, Any

from docstring_parser import parse
from langchain.pydantic_v1 import BaseModel
from langchain.schema.output_parser import OutputParserException
from langchain.schema.runnable import RunnableWithFallbacks
from langchain.llms.base import BaseLanguageModel
from langchain.chat_models.base import BaseChatModel
from langchain.chat_models import ChatOpenAI
from langchain.schema.messages import SystemMessage, HumanMessage
from rich import print
from tiktoken import encoding_for_model


def retry_parse(retry: int):
    """
    Retry parsing the output for a given number of times.

    Raises:
    - OutputParserException: If the output cannot be parsed.
    """

    def decorator(fn):
        if asyncio.iscoroutinefunction(fn):

            @wraps(fn)
            async def async_wrapper(*args, **kwargs):
                for _ in range(retry):
                    try:
                        return await fn(*args, **kwargs)
                    except OutputParserException as e:
                        if _ == retry - 1:
                            raise e
                        await asyncio.sleep(1)

            return async_wrapper

        else:

            @wraps(fn)
            def sync_wrapper(*args, **kwargs):
                for _ in range(retry):
                    try:
                        return fn(*args, **kwargs)
                    except OutputParserException as e:
                        if _ == retry - 1:
                            raise e

            return sync_wrapper

    return decorator


def raiser(e: Exception | str) -> NoReturn:
    raise e if isinstance(e, Exception) else Exception(e)


def log(*text) -> None:
    from funcchain.config import settings

    settings.VERBOSE and print("[grey]" + " ".join(map(str, text)) + "[/grey]")


def count_tokens(text: str, model: str = "gpt-4") -> int:
    return len(encoding_for_model(model).encode(text))


def gather_llm_type(llm: Type[BaseLanguageModel], func_check: bool = False) -> str:
    if isinstance(llm, RunnableWithFallbacks):
        llm = llm.runnable
    if not isinstance(llm, BaseChatModel):
        return "base_model"
    if not isinstance(llm, ChatOpenAI):
        return "chat_model"
    try:
        if func_check:
            llm.predict_messages(
                [
                    SystemMessage(content="You are an AI assistant."),
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
    except Exception as e:
        return "openai_model"
    else:
        return "function_model"


FUNCTION_MODEL = None


def is_function_model(llm: Type[BaseLanguageModel]) -> bool:
    global FUNCTION_MODEL
    if FUNCTION_MODEL is None:
        FUNCTION_MODEL = gather_llm_type(llm, True) == "function_model"
    return FUNCTION_MODEL


def _remove_a_key(d, remove_key) -> None:
    """Remove a key from a dictionary recursively"""
    if isinstance(d, dict):
        for key in list(d.keys()):
            if key == remove_key and "type" in d.keys():
                del d[key]
            else:
                _remove_a_key(d[key], remove_key)


def pydantic_to_functions(pydantic_object: Type[BaseModel]) -> dict[str, Any]:
    schema = pydantic_object.schema()
    docstring = parse(pydantic_object.__doc__ or "")
    parameters = {k: v for k, v in schema.items() if k not in ("title", "description")}
    for param in docstring.params:
        if (name := param.arg_name) in parameters["properties"] and (
            description := param.description
        ):
            if "description" not in parameters["properties"][name]:
                parameters["properties"][name]["description"] = description

    parameters["required"] = sorted(
        k for k, v in parameters["properties"].items() if not "default" in v
    )
    parameters["type"] = "object"

    if "description" not in schema:
        if docstring.short_description:
            schema["description"] = docstring.short_description
        else:
            schema["description"] = (
                f"Correctly extracted `{pydantic_object.__name__.lower()}` with all "
                f"the required parameters with correct types"
            )

    _remove_a_key(parameters, "title")
    _remove_a_key(parameters, "additionalProperties")

    return {
        "function_call": {
            "name": pydantic_object.__name__.lower(),
        },
        "functions": [
            {
                "name": pydantic_object.__name__.lower(),
                "description": schema["description"],
                "parameters": parameters,
            },
        ],
    }
