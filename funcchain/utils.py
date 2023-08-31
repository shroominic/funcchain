import asyncio
from functools import wraps
from typing import NoReturn

from langchain.schema import OutputParserException
from tiktoken import encoding_for_model
from funcchain import settings


def raiser(e: Exception | str) -> NoReturn:
    if isinstance(e, Exception):
        raise e
    else:
        raise Exception(e)


def log(*text) -> None:
    if settings.VERBOSE:
        print(*text)


def retry(retry: int):
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


def count_tokens(text: str, model: str = "gpt-4") -> int:
    return len(encoding_for_model(model).encode(text))
