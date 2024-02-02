from typing import NoReturn


def raiser(e: Exception | str) -> NoReturn:
    raise e if isinstance(e, Exception) else Exception(e)
