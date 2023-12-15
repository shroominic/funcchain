from string import Formatter
from typing import Any, Optional, Type

from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import BaseStringMessagePromptTemplate, MessagePromptTemplateT
from langchain.prompts.prompt import PromptTemplate
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.schema.chat_history import BaseChatMessageHistory
from PIL import Image
from pydantic import BaseModel

from ..utils import image_to_base64_url


def create_instruction_prompt(
    instruction: str,
    images: list[Image.Image],
    input_kwargs: dict[str, Any],
) -> "HumanImageMessagePromptTemplate":
    template_format = _determine_format(instruction)

    required_f_str_vars = _extract_fstring_vars(instruction)

    _filter_fstring_vars(input_kwargs)

    inject_vars = [
        f"{var.upper()}:\n{{{var}}}\n"
        for var, _ in input_kwargs.items()
        if var not in required_f_str_vars
    ]
    added_instruction = "\n".join(inject_vars)
    instruction = added_instruction + instruction

    images = [image_to_base64_url(image) for image in images]

    return HumanImageMessagePromptTemplate.from_template(
        template=instruction,
        template_format=template_format,
        images=images,
    )


def create_chat_prompt(
    system: str,
    instruction_template: "HumanImageMessagePromptTemplate",
    context: list[BaseMessage],
    memory: BaseChatMessageHistory,
) -> ChatPromptTemplate:
    """
    Compose a chat prompt from a system message,
    context and instruction template.
    """
    # remove leading system message in case to not have two
    if system and memory.messages and isinstance(memory.messages[0], SystemMessage):
        memory.messages.pop(0)

    if memory.messages and isinstance(memory.messages[-1], HumanMessage):
        return ChatPromptTemplate.from_messages(
            [
                *([SystemMessage(content=system)] if system else []),
                *memory.messages,
                *context,
            ]
        )

    return ChatPromptTemplate.from_messages(
        [
            *([SystemMessage(content=system)] if system else []),
            *memory.messages,
            *context,
            instruction_template,
        ]
    )


def _determine_format(
    instruction: str,
) -> str:
    return "jinja2" if "{{" in instruction or "{%" in instruction else "f-string"


def _extract_fstring_vars(template: str) -> list[str]:
    """
    TODO: enable jinja2 check
    Function to extract f-string variables from a string.
    """
    return [
        field_name  # print("field_name:", field_name) or field_name.split(".")[0]
        for _, field_name, _, _ in Formatter().parse(template)
        if field_name is not None
    ]


def _filter_fstring_vars(
    input_kwargs: dict[str, Any],
) -> None:
    """Mutate input_kwargs to filter out non-string values."""
    keys_to_remove = [
        key
        for key, value in input_kwargs.items()
        if not (
            isinstance(value, str) or isinstance(value, BaseModel)
        )  # TODO: remove BaseModel
    ]
    for key in keys_to_remove:
        del input_kwargs[key]


class HumanImageMessagePromptTemplate(BaseStringMessagePromptTemplate):
    """Human message prompt template. This is a message sent from the user."""

    images: list[str] = []

    def format(self, **kwargs: Any) -> BaseMessage:
        """Format the prompt template.

        Args:
            **kwargs: Keyword arguments to use for formatting.

        Returns:
            Formatted message.
        """
        text = self.prompt.format(**kwargs)
        return HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": text,
                },
                *[
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image,
                            "detail": "auto",
                        },
                    }
                    for image in self.images
                ],
            ],
            additional_kwargs=self.additional_kwargs,
        )

    @classmethod
    def from_template(
        cls: Type[MessagePromptTemplateT],
        template: str,
        template_format: str = "f-string",
        partial_variables: Optional[dict[str, Any]] = None,
        images: list[str] = [],
        **kwargs: Any,
    ) -> MessagePromptTemplateT:
        """Create a class from a string template.

        Args:
            template: a template.
            template_format: format of the template.
            **kwargs: keyword arguments to pass to the constructor.

        Returns:
            A new instance of this class.
        """
        prompt = PromptTemplate.from_template(
            template,
            template_format=template_format,
            partial_variables=partial_variables,
        )
        kwargs["images"] = images
        return cls(prompt=prompt, **kwargs)
