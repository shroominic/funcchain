from types import FunctionType
from typing import Callable, Optional, TypeVar, Union, overload

from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable

from ..backend.compiler import compile_chain
from ..backend.meta_inspect import gather_signature
from ..backend.settings import SettingsOverride, create_local_settings
from ..schema.signature import Signature

OutputT = TypeVar("OutputT")


@overload
def runnable(
    f: Callable[..., OutputT],
) -> Runnable[dict[str, str], OutputT]:
    ...


@overload
def runnable(
    *,
    llm: BaseChatModel | str | None = None,
    settings: SettingsOverride = {},
    auto_tune: bool = False,
) -> Callable[[Callable], Runnable[dict[str, str], OutputT]]:
    ...


def runnable(
    f: Optional[Callable[..., OutputT]] = None,
    *,
    llm: BaseChatModel | str | None = None,
    settings: SettingsOverride = {},
    auto_tune: bool = False,
) -> Union[Callable, Runnable]:
    """Decorator for funcchain syntax.
    Compiles the function into a runnable.
    """
    if llm:
        settings["llm"] = llm

    def decorator(f: Callable) -> Runnable:
        if not isinstance(f, FunctionType):
            raise ValueError("funcchain can only be used on functions")

        _signature: dict = gather_signature(f)
        _signature["settings"] = create_local_settings(override=settings)
        _signature["auto_tune"] = auto_tune

        sig: Signature = Signature(**_signature)
        return compile_chain(sig)

    if callable(f):
        return decorator(f)
    else:
        return decorator
