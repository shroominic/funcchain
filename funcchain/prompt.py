from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import BaseMessage, SystemMessage

from funcchain import settings
from funcchain.utils import count_tokens


def create_prompt(
    instruction: str,
    system: str,
    context: list[BaseMessage] = [],
    **input_kwargs,
) -> ChatPromptTemplate:
    """
    Helper to create a prompt from an instruction and a system message.
    """
    base_tokens = count_tokens(instruction + system)
    for k, v in input_kwargs.copy().items():
        if isinstance(v, str):
            content_tokens = count_tokens(v)
            if base_tokens + content_tokens > settings.MAX_TOKENS:
                input_kwargs[k] = v[: (settings.MAX_TOKENS - base_tokens) * 2 // 3]
                print("Truncated: ", len(input_kwargs[k]))

    return ChatPromptTemplate.from_messages(
        [SystemMessage(content=system)]
        + context
        + [
            HumanMessagePromptTemplate.from_template(
                template=instruction,
                template_format="jinja2" if "{{" in instruction else "f-string",
            )
            if isinstance(instruction, str)
            else instruction
        ]
    )
