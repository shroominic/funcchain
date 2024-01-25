from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import BaseGenerationOutputParser, BaseOutputParser, StrOutputParser
from pydantic import BaseModel

from ..parser.json_schema import RetryJsonPydanticParser, RetryJsonPydanticUnionParser
from ..parser.parsers import BoolOutputParser
from ..syntax.output_types import ParserBaseModel


def parser_for(
    output_types: tuple[type],
    retry: int,
    llm: BaseChatModel | str | None = None,
) -> BaseOutputParser | BaseGenerationOutputParser:
    """
    Get the parser from the type annotation of the parent caller function.
    """
    if len(output_types) > 1:
        return RetryJsonPydanticUnionParser(output_types=output_types)

    output_type = output_types[0]

    if output_type is str:
        return StrOutputParser()

    if output_type is bool:
        return BoolOutputParser()

    if issubclass(output_type, ParserBaseModel):
        return output_type.output_parser()  # type: ignore

    if issubclass(output_type, BaseModel):
        return RetryJsonPydanticParser(pydantic_object=output_type, retry=retry, retry_llm=llm)

    else:
        raise SyntaxError(f"Output Type is not supported: {output_type}")
