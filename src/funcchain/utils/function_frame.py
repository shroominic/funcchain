import types
from inspect import FrameInfo, currentframe, getouterframes
from typing import Union

from langchain.schema import BaseOutputParser, StrOutputParser

from ..parser import BoolOutputParser, ParserBaseModel, PydanticOutputParser

FUNC_DEPTH = 8


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


def from_docstring() -> str:
    """
    Get the docstring of the parent caller function.
    """
    if doc_str := get_func_obj().__doc__:
        return "\n".join([line.lstrip() for line in doc_str.split("\n")])
    raise ValueError(
        f"The funcchain ({get_parent_frame().function}) must have a docstring"
    )


def get_output_type() -> type:
    """
    Get the output type annotation of the parent caller function.
    """
    try:
        # print(get_parent_frame().frame.f_globals)
        return get_func_obj().__annotations__["return"]
    except KeyError:
        raise ValueError("The funcchain must have a return type annotation")


def parser_for(output_type: type) -> BaseOutputParser:
    """
    Get the parser from the type annotation of the parent caller function.
    """
    if isinstance(output_type, types.UnionType):
        return None  # type: ignore  # TODO: fix
    #     return MultiPydanticOutputParser(pydantic_objects=output_type.__args__)
    if getattr(output_type, "__origin__", None) is Union:
        output_type = output_type.__args__[0]  # type: ignore
        return None  # type: ignore  # TODO: fix
    #     return MultiPydanticOutputParser(pydantic_objects=output_type.__args__)
    if output_type is str:
        return StrOutputParser()
    if output_type is bool:
        return BoolOutputParser()
    if issubclass(output_type, ParserBaseModel):
        return output_type.output_parser()  # type: ignore

    from pydantic import BaseModel

    if issubclass(output_type, BaseModel):
        return PydanticOutputParser(pydantic_object=output_type)
    else:
        raise RuntimeError(f"Output Type is not supported: {output_type}")


def kwargs_from_parent() -> dict[str, str]:
    """
    Get the kwargs from the parent function.
    """
    return get_parent_frame(FUNC_DEPTH - 1).frame.f_locals
