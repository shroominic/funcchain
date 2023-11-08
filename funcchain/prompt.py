from string import Formatter

from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import BaseMessage, SystemMessage

from funcchain.utils import count_tokens


def create_prompt(
    instruction: str,
    system: str,
    context: list[BaseMessage] = [],
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
    # check if instruction is a jinja2 template
    template_format = "jinja2" if "{{" in instruction or "{%" in instruction else "f-string"
    # Extract all the f-string template variables from instruction
    required_f_str_vars = extract_fstring_vars(instruction)  # TODO: jinja2
    # get all input_kwargs that are not required by the template
    inject_vars = [f"[{var}]:\n{value}\n" for var, value in input_kwargs.items() if var not in required_f_str_vars]
    added_instruction = ("".join(inject_vars)).replace("{", "{{").replace("}", "}}")
    instruction = added_instruction + instruction

    return ChatPromptTemplate.from_messages(
        [SystemMessage(content=system)]
        + context
        + [
            HumanMessagePromptTemplate.from_template(
                template=instruction,
                template_format=template_format,
            )
        ]
    )


def extract_fstring_vars(template: str) -> list[str]:
    """
    Function to extract f-string variables from a string.
    """
    return [field_name for _, field_name, _, _ in Formatter().parse(template) if field_name is not None]
