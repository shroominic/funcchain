from typing import Any

from docstring_parser import parse
from pydantic import BaseModel


def _remove_a_key(d: dict, remove_key: str) -> None:
    """Remove a key from a dictionary recursively"""
    if isinstance(d, dict):
        for key in list(d.keys()):
            if key == remove_key and "type" in d.keys():
                del d[key]
            else:
                _remove_a_key(d[key], remove_key)


def pydantic_to_functions(pydantic_type: type[BaseModel]) -> dict[str, Any]:
    schema = pydantic_type.model_json_schema()

    docstring = parse(pydantic_type.__doc__ or "")
    parameters = {k: v for k, v in schema.items() if k not in ("title", "description")}

    for param in docstring.params:
        if (name := param.arg_name) in parameters["properties"] and (description := param.description):
            if "description" not in parameters["properties"][name]:
                parameters["properties"][name]["description"] = description

    parameters["type"] = "object"

    if "description" not in schema:
        if docstring.short_description:
            schema["description"] = docstring.short_description
        else:
            schema["description"] = (
                f"Correctly extracted `{pydantic_type.__name__.lower()}` with all "
                f"the required parameters with correct types"
            )

    _remove_a_key(parameters, "title")
    _remove_a_key(parameters, "additionalProperties")

    return {
        "function_call": {
            "name": pydantic_type.__name__.lower(),
        },
        "functions": [
            {
                "name": pydantic_type.__name__.lower(),
                "description": schema["description"],
                "parameters": parameters,
            },
        ],
    }


def multi_pydantic_to_functions(
    pydantic_types: list[type[BaseModel]],
) -> dict[str, Any]:
    functions: list[dict[str, Any]] = [
        pydantic_to_functions(pydantic_type)["functions"][0] for pydantic_type in pydantic_types
    ]

    return {
        "function_call": "auto",
        "functions": functions,
    }
