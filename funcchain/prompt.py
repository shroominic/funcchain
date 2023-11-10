from string import Formatter
from PIL import Image  # type: ignore

from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import BaseStringMessagePromptTemplate, MessagePromptTemplateT
from langchain.schema import BaseMessage, SystemMessage, HumanMessage

from typing import (
    Any,
    Type,
)

from langchain.prompts.prompt import PromptTemplate

from funcchain.utils import count_tokens, image_to_base64_url


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
                    "type": "text", "text": text,
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
                ]
            ],
            additional_kwargs=self.additional_kwargs,
        )

    @classmethod
    def from_template(
        cls: Type[MessagePromptTemplateT],
        template: str,
        template_format: str = "f-string",
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
        prompt = PromptTemplate.from_template(template, template_format=template_format)
        kwargs["images"] = images
        return cls(prompt=prompt, **kwargs)
    

def create_prompt(
    instruction: str,
    system: str,
    context: list[BaseMessage] = [],
    images: list[Image.Image] = [],
    **input_kwargs: str,
) -> ChatPromptTemplate:
    """
    Helper to create a prompt from an instruction and a system message.
    """
    base_tokens = count_tokens(instruction + system)
    for k, v in input_kwargs.copy().items():
        if isinstance(v, str):
            from funcchain import settings  # fix circular import

            content_tokens = count_tokens(v)
            if base_tokens + content_tokens > settings.MAX_TOKENS:
                input_kwargs[k] = v[: (settings.MAX_TOKENS - base_tokens) * 2 // 3]
                print("Truncated: ", len(input_kwargs[k]))
        
    template_format = "jinja2" if "{{" in instruction or "{%" in instruction else "f-string"
    
    required_f_str_vars = extract_fstring_vars(instruction)  # TODO: jinja2
    if "format_instructions" in required_f_str_vars:
        required_f_str_vars.remove("format_instructions")

    inject_vars = [f"[{var}]:\n{value}\n" for var, value in input_kwargs.items() if var not in required_f_str_vars]
    added_instruction = ("".join(inject_vars)).replace("{", "{{").replace("}", "}}")
    instruction = added_instruction + instruction

    images = [image_to_base64_url(image) for image in images]
    
    return ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=system),
            *context,
            HumanImageMessagePromptTemplate.from_template(
                template=instruction,
                template_format=template_format,
                images=images,
            )
        ]
    )


def extract_fstring_vars(template: str) -> list[str]:
    """
    Function to extract f-string variables from a string.
    """
    return [field_name for _, field_name, _, _ in Formatter().parse(template) if field_name is not None]
