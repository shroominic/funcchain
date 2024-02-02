from contextlib import asynccontextmanager, contextmanager
from contextvars import ContextVar
from typing import Any, AsyncGenerator, Awaitable, Callable, Coroutine, Generator
from uuid import UUID

from langchain_core.callbacks.base import AsyncCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatGenerationChunk, GenerationChunk, LLMResult


class AsyncStreamHandler(AsyncCallbackHandler):
    """Async callback handler that can be used to handle callbacks from langchain_core."""

    def __init__(self, fn: Callable[[str], Awaitable[None] | None], default_kwargs: dict) -> None:
        self.fn = fn
        self.default_kwargs = default_kwargs
        self.cost: float = 0.0
        self.tokens: int = 0

    async def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[BaseMessage]],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        # from .utils import count_tokens
        # for lists in messages:
        #     for message in lists:
        #         if message.content:
        #             if isinstance(message.content, str):
        #                 self.tokens += count_tokens(message.content)
        #             elif isinstance(message.content, list):
        #                 print("token_counting", message.content)
        #                 # self.tokens += count_tokens(message)
        pass

    async def on_llm_new_token(
        self,
        token: str,
        *,
        chunk: GenerationChunk | ChatGenerationChunk | None = None,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        if isinstance(self.fn, Coroutine):
            await self.fn(token, **self.default_kwargs)
        else:
            self.fn(token, **self.default_kwargs)

    async def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        if self.fn is print:
            print("\n")


stream_handler: ContextVar[AsyncStreamHandler | None] = ContextVar("stream_handler", default=None)


@contextmanager
def stream_to(fn: Callable[[str], None], **kwargs: Any) -> Generator[AsyncStreamHandler, None, None]:
    """
    Stream the llm tokens to a given function.

    Example:
        >>> with stream_to(print):
        ...     # your chain calls here
    """
    import builtins

    import rich

    if (fn is builtins.print or fn is rich.print) and kwargs == {}:
        kwargs = {"end": "", "flush": True}

    cb = AsyncStreamHandler(fn, kwargs)
    stream_handler.set(cb)
    yield cb
    stream_handler.set(None)


@asynccontextmanager
async def astream_to(
    fn: Callable[[str], Awaitable[None] | None], **kwargs: Any
) -> AsyncGenerator[AsyncStreamHandler, None]:
    """
    Asyncronously stream the llm tokens to a given function.

    Example:
        >>> async with astream_to(print):
        ...     # your chain calls here
    """
    if fn is print and kwargs == {}:
        kwargs = {"end": "", "flush": True}
    cb = AsyncStreamHandler(fn, kwargs)
    stream_handler.set(cb)
    yield cb
    stream_handler.set(None)
