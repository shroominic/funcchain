from inspect import FrameInfo, currentframe, getouterframes
from types import FunctionType, UnionType
from typing import Any, Optional

FUNC_DEPTH = 4


def get_parent_frame(depth: int = FUNC_DEPTH) -> FrameInfo:
    """
    Get the dep'th parent function information.
    """
    return getouterframes(currentframe())[depth]


def get_func_obj() -> FunctionType:
    """
    Get the parent caller function.
    """
    func_name = get_parent_frame().function
    if func_name == "<module>":
        raise RuntimeError("Cannot get function object from module")
    if func_name == "<lambda>":
        raise RuntimeError("Cannot get function object from lambda")

    try:
        func = get_parent_frame().frame.f_globals[func_name]
    except KeyError:
        func = get_parent_frame(FUNC_DEPTH + 1).frame.f_locals[func_name]
    return func


def from_docstring(f: Optional[FunctionType] = None) -> str:
    """
    Get the docstring of the parent caller function.
    """
    if doc_str := (f or get_func_obj()).__doc__:
        return "\n".join([line.lstrip() for line in doc_str.split("\n")])
    raise ValueError(f"The funcchain ({get_parent_frame().function}) must have a docstring")


def get_output_types(f: Optional[FunctionType] = None) -> list[type]:
    """
    Get the output type annotation of the parent caller function.
    Returns a list of types in case of a union, otherwise a list with one type.
    """
    try:
        return_type = (f or get_func_obj()).__annotations__["return"]
        if isinstance(return_type, UnionType):
            return return_type.__args__  # type: ignore
        else:
            return [return_type]
    except KeyError:
        raise ValueError("The funcchain must have a return type annotation")


def kwargs_from_parent() -> dict[str, Any]:
    """
    Get the kwargs from the parent function.
    """
    return get_parent_frame(FUNC_DEPTH - 1).frame.f_locals


def args_from_parent() -> list[tuple[str, type]]:
    """
    Get input args with type hints from parent function
    """
    return [(arg, t) for arg, t in get_func_obj().__annotations__.items() if arg != "return" and arg != "self"]


def gather_signature(
    f: FunctionType,
) -> dict[str, str | list[tuple[str, type]] | list[type]]:
    """
    Gather the signature of the parent caller function.
    """
    return {
        "instruction": from_docstring(f),
        "input_args": [(arg, f.__annotations__[arg]) for arg in f.__code__.co_varnames[: f.__code__.co_argcount]],
        "output_types": get_output_types(f),
    }
