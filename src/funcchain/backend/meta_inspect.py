import types
from inspect import FrameInfo, currentframe, getouterframes
from typing import Any, Optional

FUNC_DEPTH = 4


def get_parent_frame(depth: int = FUNC_DEPTH) -> FrameInfo:
    """
    Get the dep'th parent function information.
    """
    return getouterframes(currentframe())[depth]


def get_func_obj() -> types.FunctionType:
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


def from_docstring(f: Optional[types.FunctionType] = None) -> str:
    """
    Get the docstring of the parent caller function.
    """
    if doc_str := (f or get_func_obj()).__doc__:
        return "\n".join([line.lstrip() for line in doc_str.split("\n")])
    raise ValueError(f"The funcchain ({get_parent_frame().function}) must have a docstring")


def get_output_type(f: Optional[types.FunctionType] = None) -> type:
    """
    Get the output type annotation of the parent caller function.
    """
    try:
        return (f or get_func_obj()).__annotations__["return"]
    except KeyError:
        raise ValueError("The funcchain must have a return type annotation")


def kwargs_from_parent() -> dict[str, str]:
    """
    Get the kwargs from the parent function.
    """
    return get_parent_frame(FUNC_DEPTH - 1).frame.f_locals


def gather_signature(f: types.FunctionType) -> dict[str, Any]:
    """
    Gather the signature of the parent caller function.
    """
    return {
        "instruction": from_docstring(f),
        "input_args": list(f.__code__.co_varnames[: f.__code__.co_argcount]),
        "output_type": get_output_type(f),
    }
