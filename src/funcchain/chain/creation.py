from types import UnionType
from typing import TypeVar, Union

from langchain.chat_models.base import BaseChatModel
from langchain.prompts import ChatPromptTemplate
from langchain.schema import (
    AIMessage,
    BaseMessage,
    BaseOutputParser,
    HumanMessage,
)
from langchain.schema.chat_history import BaseChatMessageHistory
from langchain.schema.runnable import (
    RunnableSequence,
    RunnableWithFallbacks,
    RunnableSerializable,
)
from PIL import Image
from pydantic import BaseModel

from ..settings import settings, FuncchainSettings
from ..streaming import stream_handler
from ..parser import MultiToolParser, ParserBaseModel, PydanticFuncParser
from ..utils import (
    from_docstring,
    get_output_type,
    is_function_model,
    is_vision_model,
    kwargs_from_parent,
    model_from_env,
    multi_pydantic_to_functions,
    pydantic_to_functions,
    count_tokens,
    parser_for,
)
from .prompt import (
    create_chat_prompt,
    create_instruction_prompt,
    HumanImageMessagePromptTemplate,
)


ChainOutput = TypeVar("ChainOutput")


# TODO: do patch instead of seperate creation
def create_union_chain(
    output_type: type[BaseModel],
    instruction_prompt: HumanImageMessagePromptTemplate,
    system: str,
    memory: BaseChatMessageHistory,
    context: list[BaseMessage],
    LLM: BaseChatModel | RunnableWithFallbacks,
    input_kwargs: dict[str, str],
) -> RunnableSequence[dict[str, str], ChainOutput]:
    output_types = output_type.__args__  # type: ignore
    output_type_names = [t.__name__ for t in output_types]

    input_kwargs[
        "format_instructions"
    ] = f"Extract to one of these output types: {output_type_names}."

    functions = multi_pydantic_to_functions(output_types)

    if isinstance(LLM, RunnableWithFallbacks):
        LLM = LLM.runnable.bind(**functions).with_fallbacks(
            [
                fallback.bind(**functions)
                for fallback in LLM.fallbacks
                if hasattr(LLM, "fallbacks")
            ]
        )
    else:
        LLM = LLM.bind(**functions)  # type: ignore

    prompt = create_chat_prompt(
        system,
        instruction_prompt,
        context=[
            *context,
            HumanMessage(content="Can you use a function call for the next response?"),
            AIMessage(content="Yeah I can do that, just tell me what you need!"),
        ],
        memory=memory,
    )

    return prompt | LLM | MultiToolParser(output_types=output_types)  # type: ignore


# TODO: do patch instead of seperate creation
def create_pydanctic_chain(
    output_type: type[BaseModel],
    prompt: ChatPromptTemplate,
    LLM: BaseChatModel | RunnableWithFallbacks,
    input_kwargs: dict[str, str],
) -> RunnableSequence[dict[str, str], ChainOutput]:
    # TODO: check these format_instructions
    input_kwargs["format_instructions"] = f"Extract to {output_type.__name__}."
    functions = pydantic_to_functions(output_type)
    LLM = (
        LLM.runnable.bind(**functions).with_fallbacks(  # type: ignore
            [
                fallback.bind(**functions)
                for fallback in LLM.fallbacks
                if hasattr(LLM, "fallbacks")
            ]
        )
        if isinstance(LLM, RunnableWithFallbacks)
        else LLM.bind(**functions)
    )
    return prompt | LLM | PydanticFuncParser(pydantic_schema=output_type)  # type: ignore


def create_chain(
    system: str | None,
    instruction: str | None,
    parser: BaseOutputParser[ChainOutput] | None,
    context: list[BaseMessage],
    memory: BaseChatMessageHistory,
    input_kwargs: dict[str, str],
) -> RunnableSerializable[dict[str, str], ChainOutput]:
    """
    Compile a langchain runnable chain from the funcchain syntax.
    """
    # default values
    output_type = get_output_type()
    input_kwargs.update(kwargs_from_parent())
    system = system or settings.DEFAULT_SYSTEM_PROMPT
    instruction = instruction or from_docstring()
    parser = parser or parser_for(output_type)

    # large language model
    llm = _gather_llm(settings)

    # add format instructions for parser
    if parser and not is_function_model(llm):
        instruction = _add_format_instructions(
            parser,
            instruction,
            input_kwargs,
        )

    # patch inputs
    _crop_large_inputs(
        system,
        instruction,
        input_kwargs,
    )

    # for vision models
    images = _handle_images(llm, input_kwargs)

    # create prompts
    instruction_prompt = create_instruction_prompt(instruction, images, input_kwargs)
    chat_prompt = create_chat_prompt(system, instruction_prompt, context, memory)

    # add formatted instruction to chat history
    memory.add_message(instruction_prompt.format(**input_kwargs))

    # function model patches
    if is_function_model(llm):
        if getattr(output_type, "__origin__", None) is Union or isinstance(
            output_type, UnionType
        ):
            return create_union_chain(
                output_type,
                instruction_prompt,
                system,
                memory,
                context,
                llm,
                input_kwargs,
            )

        if issubclass(output_type, BaseModel) and not issubclass(
            output_type, ParserBaseModel
        ):
            return create_pydanctic_chain(
                output_type,
                chat_prompt,
                llm,
                input_kwargs,
            )

    return chat_prompt | llm | parser


def _add_format_instructions(
    parser: BaseOutputParser,
    instruction: str,
    input_kwargs: dict[str, str],
) -> str:
    """
    Add parsing format instructions
    to the instruction message and input_kwargs
    if the output parser supports it.
    """
    try:
        if format_instructions := parser.get_format_instructions():
            instruction += "\n{format_instructions}"
            input_kwargs["format_instructions"] = format_instructions
        return instruction
    except NotImplementedError:
        return instruction


def _crop_large_inputs(
    system: str,
    instruction: str,
    input_kwargs: dict,
) -> None:
    """
    TODO: replace MAX_TOKENS with MAX_CONTENT_LENGTH
    Crop large inputs to avoid exceeding the maximum number of tokens.
    """
    base_tokens = count_tokens(instruction + system)
    for k, v in input_kwargs.copy().items():
        if isinstance(v, str):
            from funcchain import settings

            content_tokens = count_tokens(v)
            if base_tokens + content_tokens > settings.MAX_TOKENS:
                input_kwargs[k] = v[: (settings.MAX_TOKENS - base_tokens) * 2 // 3]
                print("Truncated: ", len(input_kwargs[k]))


def _handle_images(
    LLM: BaseChatModel | RunnableWithFallbacks,
    input_kwargs: dict[str, str],
) -> list[Image.Image]:
    """
    Handle images for vision models.
    """
    images = [v for v in input_kwargs.values() if isinstance(v, Image.Image)]
    if is_vision_model(LLM):
        input_kwargs = {
            k: v for k, v in input_kwargs.items() if not isinstance(v, Image.Image)
        }
    elif images:
        raise RuntimeError("Images as input are only supported for vision models.")

    return images


def _gather_llm(
    settings: FuncchainSettings,
) -> BaseChatModel | RunnableWithFallbacks:
    llm = settings.LLM or model_from_env()
    if not llm:
        raise RuntimeError(
            "No language model provided. Either set the LLM environment variable or "
            "pass a model to the `chain` function."
        )
    if handler := stream_handler.get():
        if isinstance(llm, RunnableWithFallbacks) and isinstance(
            llm.runnable, BaseChatModel
        ):
            llm.runnable.callbacks = [handler]
        elif isinstance(llm, BaseChatModel):
            llm.callbacks = [handler]
    return llm
