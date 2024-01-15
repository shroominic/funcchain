from types import UnionType
from typing import Type, TypeVar

from langchain_core.callbacks import Callbacks
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import BaseGenerationOutputParser, BaseOutputParser
from langchain_core.runnables import Runnable
from PIL import Image
from pydantic import BaseModel

from ..model.abilities import is_openai_function_model, is_vision_model
from ..model.defaults import univeral_model_selector
from ..parser.openai_functions import OpenAIFunctionPydanticParser, OpenAIFunctionPydanticUnionParser
from ..parser.schema_converter import pydantic_to_grammar
from ..parser.selector import parser_for
from ..schema.signature import Signature
from ..syntax.output_types import ParserBaseModel
from ..utils.msg_tools import msg_to_str
from ..utils.pydantic import multi_pydantic_to_functions, pydantic_to_functions
from ..utils.token_counter import count_tokens
from .prompt import (
    HumanImageMessagePromptTemplate,
    create_chat_prompt,
    create_instruction_prompt,
)
from .settings import FuncchainSettings
from .streaming import stream_handler

ChainOutput = TypeVar("ChainOutput")


# TODO: do patch instead of seperate creation
def create_union_chain(
    output_type: UnionType,
    instruction_prompt: HumanImageMessagePromptTemplate,
    system: str,
    memory: BaseChatMessageHistory,
    context: list[BaseMessage],
    llm: BaseChatModel,
    input_kwargs: dict[str, str],
) -> Runnable[dict[str, str], BaseModel]:
    """
    Compile a langchain runnable chain from the funcchain syntax.
    """
    if not all(issubclass(t, BaseModel) for t in output_type.__args__):
        raise RuntimeError("Funcchain union types are currently only supported for pydantic models.")

    output_types: list[Type[BaseModel]] = output_type.__args__  # type: ignore
    output_type_names = [t.__name__ for t in output_types]

    input_kwargs["format_instructions"] = f"Extract to one of these output types: {output_type_names}."

    functions = multi_pydantic_to_functions(output_types)

    llm = llm.bind(**functions)  # type: ignore

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

    return prompt | llm | OpenAIFunctionPydanticUnionParser(output_types=output_types)


def parse_function_to_pydantic(
    llm: BaseChatModel,
    output_type: type[BaseModel],
    input_kwargs: dict[str, str],
) -> BaseGenerationOutputParser:
    input_kwargs["format_instructions"] = f"Extract to {output_type.__name__}."
    functions = pydantic_to_functions(output_type)

    llm = llm.bind(**functions)  # type: ignore

    return OpenAIFunctionPydanticParser(pydantic_schema=output_type)


def create_chain(
    system: str,
    instruction: str,
    output_type: Type[ChainOutput],
    context: list[BaseMessage],
    memory: BaseChatMessageHistory,
    settings: FuncchainSettings,
    input_kwargs: dict[str, str],
) -> Runnable[dict[str, str], ChainOutput]:
    """
    Compile a langchain runnable chain from the funcchain syntax.
    """
    # large language model
    _llm = _gather_llm(settings)
    llm = _add_custom_callbacks(_llm, settings)

    parser = parser_for(output_type, retry=settings.retry_parse, llm=llm)

    # add format instructions for parser
    f_instructions = None
    if parser and (settings.streaming or not is_openai_function_model(llm)):
        # streaming behavior is not supported for function models
        # but for normal function models we do not need to add format instructions
        if not isinstance(parser, BaseOutputParser):
            raise NotImplementedError("Fix this")
        instruction, f_instructions = _add_format_instructions(
            parser,
            instruction,
            input_kwargs,
        )

    # patch inputs
    _crop_large_inputs(
        system,
        instruction,
        input_kwargs,
        settings,
    )

    # for vision models
    images = _handle_images(llm, memory, input_kwargs)

    # create prompts
    instruction_prompt = create_instruction_prompt(
        instruction,
        images,
        input_kwargs,
        format_instructions=f_instructions,
    )
    chat_prompt = create_chat_prompt(system, instruction_prompt, context, memory)

    # add formatted instruction to chat history
    memory.add_message(instruction_prompt.format(**input_kwargs))

    _inject_grammar_for_local_models(llm, output_type)

    # function model patches
    if is_openai_function_model(llm):
        if isinstance(output_type, UnionType):
            return create_union_chain(
                output_type,
                instruction_prompt,
                system,
                memory,
                context,
                llm,
                input_kwargs,
            )

        if issubclass(output_type, BaseModel) and not issubclass(output_type, ParserBaseModel):
            if settings.streaming and hasattr(llm, "model_kwargs"):
                llm.model_kwargs = {"response_format": {"type": "json_object"}}
            else:
                parser = parse_function_to_pydantic(llm, output_type, input_kwargs)

    assert parser is not None
    return chat_prompt | llm | parser


def compile_chain(signature: Signature[ChainOutput]) -> Runnable[dict[str, str], ChainOutput]:
    """
    Compile a signature to a runnable chain.
    """
    system = (
        [msg for msg in signature.history if isinstance(msg, SystemMessage)]
        or [
            SystemMessage(content=""),
        ]
    ).pop()
    input_kwargs = {k: "" for k in signature.input_args}

    from langchain.memory import ChatMessageHistory

    memory = ChatMessageHistory(messages=signature.history)

    return create_chain(
        msg_to_str(system),
        signature.instruction,
        signature.output_type,
        signature.history,
        memory,
        signature.settings,
        input_kwargs,
    )


def _add_format_instructions(
    parser: BaseOutputParser,
    instruction: str,
    input_kwargs: dict[str, str],
) -> tuple[str, str | None]:
    """
    Add parsing format instructions
    to the instruction message and input_kwargs
    if the output parser supports it.
    """
    try:
        if format_instructions := parser.get_format_instructions():
            instruction += "\n{format_instructions}"
            input_kwargs["format_instructions"] = format_instructions
        return instruction, format_instructions
    except NotImplementedError:
        return instruction, None


def _crop_large_inputs(
    system: str,
    instruction: str,
    input_kwargs: dict,
    settings: FuncchainSettings,
) -> None:
    """
    Crop large inputs to avoid exceeding the maximum number of tokens.
    """
    base_tokens = count_tokens(instruction + system)
    for k, v in input_kwargs.copy().items():
        if isinstance(v, str):
            content_tokens = count_tokens(v)
            if base_tokens + content_tokens > settings.context_lenght:
                input_kwargs[k] = v[: (settings.context_lenght - base_tokens) * 2 // 3]
                print("Truncated: ", len(input_kwargs[k]))


def _handle_images(
    llm: BaseChatModel,
    memory: BaseChatMessageHistory,
    input_kwargs: dict[str, str],
) -> list[Image.Image]:
    """
    Handle images for vision models.
    """
    images = [v for v in input_kwargs.values() if isinstance(v, Image.Image)]
    if is_vision_model(llm):
        for k in list(input_kwargs.keys()):
            if isinstance(input_kwargs[k], Image.Image):
                del input_kwargs[k]
    elif images:
        raise RuntimeError("Images as input are only supported for vision models.")
    elif _history_contains_images(memory):
        print("Warning: Images in chat history are ignored for non-vision models.")
        memory.messages = _clear_images_from_history(memory.messages)

    return images


def _inject_grammar_for_local_models(llm: BaseChatModel, output_type: type) -> None:
    """
    Inject GBNF grammar into local models.
    """
    try:
        from funcchain.model.llm_overrides import ChatOllama
    except:  # noqa
        pass
    else:
        if isinstance(llm, ChatOllama):
            if isinstance(output_type, UnionType):
                raise NotImplementedError("Union types are not yet supported for LlamaCpp models.")  # TODO: implement

            if issubclass(output_type, BaseModel) and not issubclass(output_type, ParserBaseModel):
                llm.grammar = pydantic_to_grammar(output_type)
            if issubclass(output_type, ParserBaseModel):
                llm.grammar = output_type.custom_grammar()


def _gather_llm(settings: FuncchainSettings) -> BaseChatModel:
    if isinstance(settings.llm, BaseChatModel):
        llm = settings.llm
    else:
        llm = univeral_model_selector(settings)

    if not llm:
        raise RuntimeError(
            "No language model provided. Either set the llm environment variable or "
            "pass a model to the `chain` function."
        )
    return llm


def _add_custom_callbacks(llm: BaseChatModel, settings: FuncchainSettings) -> BaseChatModel:
    callbacks: Callbacks = []

    if handler := stream_handler.get():
        callbacks = [handler]

    if settings.console_stream:
        from .streaming import AsyncStreamHandler

        callbacks = [
            AsyncStreamHandler(print, {"end": "", "flush": True}),
        ]

    if callbacks:
        settings.streaming = True
        if hasattr(llm, "streaming"):
            llm.streaming = True
        llm.callbacks = callbacks

    return llm


def _history_contains_images(history: BaseChatMessageHistory) -> bool:
    """
    Check if the chat history contains images.
    """
    for message in history.messages:
        if isinstance(message.content, list):
            for content in message.content:
                if isinstance(content, dict) and content.get("type") == "image_url":
                    return True
    return False


def _clear_images_from_history(history: list[BaseMessage]) -> list[BaseMessage]:
    """
    Remove images from the chat history.
    """
    for message in history:
        if isinstance(message.content, list):
            for content in message.content:
                if isinstance(content, dict) and content.get("type") == "image_url":
                    message.content.remove(content)
    return history
