from typing import Any
from functools import wraps
from time import sleep
from asyncio import iscoroutinefunction, sleep as asleep
from langchain.schema.output_parser import OutputParserException
from langchain.callbacks import get_openai_callback
from langchain.schema.runnable import RunnableSequence
from rich import print

from .function_frame import get_parent_frame
    

def retry_parse(fn: Any) -> Any:
    """
    Retry parsing the output for a given number of times.

    Raises:
    - OutputParserException: If the output cannot be parsed.
    """
    from ..settings import settings
    retry = settings.RETRY_PARSE
    
    if iscoroutinefunction(fn):
        @wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            for r in range(retry):
                try:
                    return await fn(*args, **kwargs)
                except OutputParserException as e:
                    if r == retry - 1:
                        raise e
                    await asleep(settings.RETRY_PARSE_SLEEP + r)

        return async_wrapper

    else:
        @wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            for r in range(retry):
                try:
                    return fn(*args, **kwargs)
                except OutputParserException as e:
                    if r == retry - 1:
                        raise e
                    sleep(settings.RETRY_PARSE_SLEEP + r)

        return sync_wrapper


def log_openai_callback(fn: Any) -> Any:
    if iscoroutinefunction(fn):
        @wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            if (chain := args[0]) and isinstance(chain, RunnableSequence):
                with get_openai_callback() as cb:
                    result = await chain.ainvoke(args[2])
                    if cb.total_tokens != 0:
                        total_cost = f"/ {cb.total_cost:.3f}$ " if cb.total_cost > 0 else ""
                        if total_cost == "/ 0.000$ ":
                            total_cost = "/ 0.001$ "
                        _log(
                            f"{cb.total_tokens:05}T {total_cost}- {get_parent_frame(4).function}"
                        )
                    return result
            return await fn(*args, **kwargs)

        return async_wrapper

    else:
        @wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            if (chain := args[0]) and isinstance(chain, RunnableSequence):
                with get_openai_callback() as cb:
                    result = chain.invoke(args[2])
                    if cb.total_tokens != 0:
                        total_cost = f"/ {cb.total_cost:.3f}$ " if cb.total_cost > 0 else ""
                        if total_cost == "/ 0.000$ ":
                            total_cost = "/ 0.001$ "
                        _log(
                            f"{cb.total_tokens:05}T {total_cost}- {get_parent_frame(4).function}"
                        )
                    return result
            return fn(*args, **kwargs)

        return sync_wrapper


def _log(*text: Any) -> None:
    from ..settings import settings
    
    if settings.DEBUG:
        print("[bright_black]" + " ".join(map(str, text)) + "[/bright_black]")
