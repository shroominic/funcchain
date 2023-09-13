import asyncio
from functools import wraps
from typing import NoReturn

from langchain.schema import OutputParserException
from tiktoken import encoding_for_model
from rich import print
from funcchain import settings


def raiser(e: Exception | str) -> NoReturn:
    raise e if isinstance(e, Exception) else Exception(e)


def log(*text) -> None:
    settings.VERBOSE and print("[grey]" + " ".join(map(str, text)) + "[/grey]")


def count_tokens(text: str, model: str = "gpt-4") -> int:
    return len(encoding_for_model(model).encode(text))


def retry_parse(retry: int):
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
