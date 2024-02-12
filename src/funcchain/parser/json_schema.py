import json
import re
from typing import Type, TypeVar

import yaml  # type: ignore
from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.runnables import Runnable
from pydantic import BaseModel, ValidationError

from ..schema.types import UniversalChatModel

M = TypeVar("M", bound=BaseModel)


class RetryJsonPydanticParser(BaseOutputParser[M]):
    """Parse an output using a pydantic model."""

    pydantic_object: Type[M]
    """The pydantic model to parse."""

    retry: int
    retry_llm: UniversalChatModel = None

    def parse(self, text: str) -> M:
        try:
            matches = re.findall(r"\{.*\}", text.strip(), re.MULTILINE | re.IGNORECASE | re.DOTALL)
            if len(matches) > 1:
                for match in matches:
                    try:
                        json_object = json.loads(match, strict=False)
                        return self.pydantic_object.model_validate(json_object)
                    except (json.JSONDecodeError, ValidationError):
                        continue
            elif len(matches) == 1:
                json_object = json.loads(matches[0], strict=False)
                return self.pydantic_object.model_validate(json_object)
            # no matches
            raise OutputParserException(
                f"No JSON {self.pydantic_object.__name__} found in completion {text}.",
                llm_output=text,
            )
        except (json.JSONDecodeError, ValidationError) as e:
            if self.retry > 0:
                print(f"Retrying parsing {self.pydantic_object.__name__}...")
                return self.retry_chain.invoke(
                    input={"output": text, "error": str(e)},
                    config={"run_name": "RetryPydanticOutputParser"},
                )
            # no retries left
            raise OutputParserException(str(e), llm_output=text)

    def get_format_instructions(self) -> str:
        schema = self.pydantic_object.model_json_schema()

        # Remove extraneous fields.
        reduced_schema = schema
        if "title" in reduced_schema:
            del reduced_schema["title"]
        if "type" in reduced_schema:
            del reduced_schema["type"]
        # Ensure json in context is well-formed with double quotes.
        schema_str = yaml.dump(reduced_schema)

        return (
            "Please respond with a json result matching the following schema:"
            f"\n\n```schema\n{schema_str}\n```\n"
            "Do not repeat the schema. Only respond with the resulting json object."
        )

    @property
    def _type(self) -> str:
        return "pydantic"

    @property
    def retry_chain(self) -> Runnable:
        from ..syntax.executable import compile_runnable

        return compile_runnable(
            instruction="Retry parsing the output by fixing the error.",
            input_args=["output", "error"],
            output_types=[self.pydantic_object],
            llm=self.retry_llm,
            settings_override={"retry_parse": self.retry - 1},
        )


class RetryJsonPydanticUnionParser(BaseOutputParser[M]):
    """Parse an output using a pydantic model."""

    output_types: list[Type[M]]

    def parse(self, text: str) -> M:
        raise NotImplementedError
