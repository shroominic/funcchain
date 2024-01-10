from typing import NoReturn

from tiktoken import encoding_for_model


def raiser(e: Exception | str) -> NoReturn:
    raise e if isinstance(e, Exception) else Exception(e)


def count_tokens(text: str, model: str = "gpt-4") -> int:
    return len(encoding_for_model(model).encode(text))
