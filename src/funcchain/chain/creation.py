from types import UnionType
from typing import TypeVar, Type

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import (
    RunnableSerializable,
    RunnableWithFallbacks,
)
from PIL import Image
from pydantic import BaseModel

from funcchain._llms import ChatLlamaCpp

from ..parser import MultiToolParser, ParserBaseModel, PydanticFuncParser
from ..settings import FuncchainSettings
from ..streaming import stream_handler
from ..utils import (
    parser_for,
    count_tokens,
    is_function_model,
    is_vision_model,
    multi_pydantic_to_functions,
    pydantic_to_functions,
    pydantic_to_grammar,
    univeral_model_selector,
)
from .prompt import (
    HumanImageMessagePromptTemplate,
    create_chat_prompt,
    create_instruction_prompt,
)

ChainOutput = TypeVar("ChainOutput")


# TODO: do patch instead of seperate creation
def create_union_chain(
    output_type: UnionType,
    instruction_prompt: HumanImageMessagePromptTemplate,
    system: str,
    memory: BaseChatMessageHistory,
    context: list[BaseMessage],
    llm: BaseChatModel | RunnableWithFallbacks,
    input_kwargs: dict[str, str],
) -> RunnableSerializable[dict[str, str], BaseModel]:
    """
    Compile a langchain runnable chain from the funcchain syntax.
    """
    if not all(issubclass(t, BaseModel) for t in output_type.__args__):
        raise RuntimeError(
            "Funcchain union types are currently only supported for pydantic models."
        )

    output_types: list[Type[BaseModel]] = output_type.__args__  # type: ignore
    output_type_names = [t.__name__ for t in output_types]

    input_kwargs[
        "format_instructions"
    ] = f"Extract to one of these output types: {output_type_names}."

    functions = multi_pydantic_to_functions(output_types)

    if isinstance(llm, RunnableWithFallbacks):
        llm = llm.runnable.bind(**functions).with_fallbacks(
            [
                fallback.bind(**functions)
                for fallback in llm.fallbacks
                if hasattr(llm, "fallbacks")
            ]
        )
    else:
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

    return prompt | llm | MultiToolParser(output_types=output_types)


# TODO: do patch instead of seperate creation
def create_pydanctic_chain(
    output_type: type[BaseModel],
    prompt: ChatPromptTemplate,
    llm: BaseChatModel | RunnableWithFallbacks,
    input_kwargs: dict[str, str],
) -> RunnableSerializable[dict[str, str], BaseModel]:
    # TODO: check these format_instructions
    input_kwargs["format_instructions"] = f"Extract to {output_type.__name__}."
    functions = pydantic_to_functions(output_type)

    llm = (
        llm.runnable.bind(**functions).with_fallbacks(  # type: ignore
            [
                fallback.bind(**functions)
                for fallback in llm.fallbacks
                if hasattr(llm, "fallbacks")
            ]
        )
        if isinstance(llm, RunnableWithFallbacks)
        else llm.bind(**functions)
    )
    return prompt | llm | PydanticFuncParser(pydantic_schema=output_type)


def create_chain(
    system: str,
    instruction: str,
    output_type: Type[ChainOutput],
    context: list[BaseMessage],
    memory: BaseChatMessageHistory,
    settings: FuncchainSettings,
    input_kwargs: dict[str, str],
) -> RunnableSerializable[dict[str, str], ChainOutput]:
    """
    Compile a langchain runnable chain from the funcchain syntax.
    """
    # large language model
    llm = _gather_llm(settings)

    parser = parser_for(output_type)

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
        settings,
    )

    # for vision models
    images = _handle_images(llm, input_kwargs)

    # create prompts
    instruction_prompt = create_instruction_prompt(instruction, images, input_kwargs)
    chat_prompt = create_chat_prompt(system, instruction_prompt, context, memory)

    # add formatted instruction to chat history
    memory.add_message(instruction_prompt.format(**input_kwargs))

    if isinstance(llm, ChatLlamaCpp):
        if isinstance(output_type, UnionType):
            # TODO: implement Union Type grammar
            raise NotImplementedError(
                "Union types are not yet supported for LlamaCpp models."
            )
        if issubclass(output_type, BaseModel) and not issubclass(
            output_type, ParserBaseModel
        ):
            from llama_cpp import LlamaGrammar

            grammar = pydantic_to_grammar(output_type)
            setattr(
                llm,
                "grammar",
                LlamaGrammar.from_string(grammar, verbose=False),
            )

    # function model patches
    if is_function_model(llm):
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

        if issubclass(output_type, BaseModel) and not issubclass(
            output_type, ParserBaseModel
        ):
            return create_pydanctic_chain(  # type: ignore
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
    llm: BaseChatModel | RunnableWithFallbacks,
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

    return images


def _gather_llm(
    settings: FuncchainSettings,
) -> BaseChatModel | RunnableWithFallbacks:
    if isinstance(settings.llm, RunnableWithFallbacks) or isinstance(
        settings.llm, BaseChatModel
    ):
        llm = settings.llm
    else:
        llm = univeral_model_selector(settings)

    if not llm:
        raise RuntimeError(
            "No language model provided. Either set the llm environment variable or "
            "pass a model to the `chain` function."
        )
    if handler := stream_handler.get():
        settings.streaming = True
        if isinstance(llm, RunnableWithFallbacks) and isinstance(
            llm.runnable, BaseChatModel
        ):
            llm.runnable.callbacks = [handler]
        elif isinstance(llm, BaseChatModel):
            llm.callbacks = [handler]
    return llm
