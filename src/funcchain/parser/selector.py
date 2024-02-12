from enum import Enum
from typing import Literal, get_origin

from langchain_core.output_parsers import BaseGenerationOutputParser, BaseOutputParser, StrOutputParser
from pydantic import BaseModel

from ..parser.json_schema import RetryJsonPydanticParser, RetryJsonPydanticUnionParser
from ..parser.primitive_types import RetryJsonPrimitiveTypeParser
from ..schema.types import UniversalChatModel
from ..syntax.output_types import ParserBaseModel


def parser_for(
    output_types: list[type],
    retry: int,
    llm: UniversalChatModel = None,
) -> BaseOutputParser | BaseGenerationOutputParser:
    """
    Get the parser from the type annotation of the parent caller function.
    """
    if len(output_types) > 1:
        return RetryJsonPydanticUnionParser(output_types=output_types)

    output_type = output_types[0]

    if output_type is str:
        return StrOutputParser()

    # TODO: write tests for each of these cases
    if (
        (output_type is bool)
        or (output_type is int)
        or (output_type is float)
        or (output_type is dict)
        or (output_type is list)
        or (output_type is tuple)
        or ((t := get_origin(output_type)) is dict)
        or (t is list)
        or (t is tuple)
        or (t is Literal)
        or (t is Enum)
    ):
        return RetryJsonPrimitiveTypeParser(primitive_type=output_type, retry=retry, retry_llm=llm)

    if issubclass(output_type, ParserBaseModel):
        return output_type.output_parser()  # type: ignore

    if issubclass(output_type, BaseModel):
        return RetryJsonPydanticParser(pydantic_object=output_type, retry=retry, retry_llm=llm)

    else:
        raise SyntaxError(f"Output Type is not supported: {output_type}")
