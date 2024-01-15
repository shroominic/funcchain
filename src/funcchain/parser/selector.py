import types
from typing import Union

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import BaseGenerationOutputParser, BaseOutputParser, StrOutputParser

from ..parser.json_schema import RetryJsonPydanticParser, RetryJsonPydanticUnionParser
from ..parser.parsers import BoolOutputParser
from ..syntax.output_types import ParserBaseModel


def parser_for(
    output_type: type,
    retry: int,
    llm: BaseChatModel | str | None = None,
) -> BaseOutputParser | BaseGenerationOutputParser:
    """
    Get the parser from the type annotation of the parent caller function.
    """
    if isinstance(output_type, types.UnionType) or getattr(output_type, "__origin__", None) is Union:
        output_type = output_type.__args__[0]  # type: ignore
        return RetryJsonPydanticUnionParser(pydantic_objects=output_type.__args__)  # type: ignore  # TODO: fix this
    if output_type is str:
        return StrOutputParser()
    if output_type is bool:
        return BoolOutputParser()
    if issubclass(output_type, ParserBaseModel):
        return output_type.output_parser()  # type: ignore

    from pydantic import BaseModel

    if issubclass(output_type, BaseModel):
        return RetryJsonPydanticParser(pydantic_object=output_type, retry=retry, retry_llm=llm)
    else:
        raise SyntaxError(f"Output Type is not supported: {output_type}")
