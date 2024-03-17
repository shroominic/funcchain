from types import FunctionType
from typing import Any, Callable, Optional, TypeVar, Union, overload

from langchain_core.runnables import Runnable

from ..backend.compiler import compile_chain
from ..backend.meta_inspect import gather_signature
from ..backend.settings import SettingsOverride, create_local_settings
from ..schema.signature import Signature
from ..schema.types import UniversalChatModel

OutputT = TypeVar("OutputT")


@overload
def runnable(
    f: Callable[..., OutputT],
) -> Runnable[dict[str, Any], OutputT]:
    ...


@overload
def runnable(
    *,
    llm: UniversalChatModel = None,
    settings: SettingsOverride = {},
) -> Callable[[Callable[..., OutputT]], Runnable[dict[str, Any], OutputT]]:
    ...


def runnable(
    f: Optional[Callable[..., OutputT]] = None,
    *,
    llm: UniversalChatModel = None,
    settings: SettingsOverride = {},
) -> Union[Callable, Runnable[dict[str, Any], OutputT]]:
    """Decorator for funcchain syntax.
    Compiles the function into a runnable.
    """
    if llm:
        settings["llm"] = llm

    def decorator(f: Callable) -> Runnable[dict[str, Any], OutputT]:
        if not isinstance(f, FunctionType):
            raise ValueError("funcchain can only be used on functions")

        _signature: dict = gather_signature(f)
        _signature["settings"] = create_local_settings(override=settings)
        # todo _signature["auto_tune"] = auto_tune

        sig: Signature = Signature(**_signature)
        return compile_chain(sig)

    if callable(f):
        return decorator(f)
    else:
        return decorator
