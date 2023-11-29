"""
llama.cpp JSON grammar
GBNF (GGML Backus-Naur Form) notation
"""
from typing import Any, Type, Generator
from contextlib import contextmanager
from pydantic import BaseModel

default_grammar: dict[str, str] = {
    "root": r'"{" ws schema ws "}\n</s>"',
    "schema": "",
    "value": 'object | array | string | number | integer | boolean | "null"',  # try to remove open values
    "object": r'"{" ws ( key ":" value ("," string ":" value)* )? "}" "\n"?',
    "array": '"[" ws ( value ("," ws value)* )? "]" ws',  # this is slow
    "key": r'"\"" [a-zA-Z0-9_]+ "\""',
    "string": r'"\"" ( [^"\\] | "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]) )* "\""',
    "number": 'integer ("." [0-9]+)? ([eE] [-+]? [0-9]+)?',
    "integer": '("-"? ([0-9] | [1-9] [0-9]*))',
    "boolean": '("true" | "false")',
    "ws": "[ \n]?",
}


def format_grammar(grammar: dict[str, str]) -> str:
    """
    Format a grammar dictionary into a string.
    """
    return "\n".join(f"{key} ::= {value}" for key, value in grammar.items())


def simple_grammar_schema_from_(pydantic_model: Type[BaseModel]) -> str:
    """
    Dynamically generate a grammar from a pydantic model.
    """
    properties: dict[str, Any] = pydantic_model.model_json_schema()["properties"]
    schema_fields = []
    for key, value in properties.items():
        field = f'"\\"{key}\\"" ":" {value.get("type", "string")}'
        schema_fields.append(field)

    return ' "," '.join(schema_fields)


def generate_grammar_schema(properties: dict[str, Any], prefix: str = "") -> str:
    """
    Recursively generate a schema from a dictionary of properties.
    """
    schema_parts = []
    for key, value in properties.items():
        if "properties" in value:
            nested_schema = generate_grammar_schema(
                value["properties"], prefix=f"{prefix}{key}."
            )
            schema_parts.append(nested_schema)
        else:
            type_ = value.get("type", "string")
            schema_parts.append(rf'"{prefix}\"{key}\"" ":" ws {type_}')
    return ' "," '.join(schema_parts)


def grammar_from_(pydantic_model: Type[BaseModel]) -> str:
    """
    Dynamically generate a grammar from a pydantic model.
    """
    grammar = default_grammar.copy()
    schema = simple_grammar_schema_from_(pydantic_model)
    grammar["schema"] = schema
    return format_grammar(grammar)


# TODO: remove when grammar field validation is fixed
@contextmanager
def grammar_file_from(pydantic_model: Type[BaseModel]) -> Generator[str, None, None]:
    from tempfile import NamedTemporaryFile

    grammar = grammar_from_(pydantic_model)
    with NamedTemporaryFile("w") as f:
        f.write(grammar)
        f.flush()
        yield f.name


if __name__ == "__main__":

    class Keyword(BaseModel):
        word: str
        rating: int

    class Poem(BaseModel):
        topic: str
        content: str
        keywords: list[Keyword]
        error: bool = False
        error_importance: int = 0

    print(simple_grammar_schema_from_(Poem))
