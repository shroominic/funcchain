from operator import itemgetter
from typing import Annotated, Any, TypeVar, get_args, get_origin

from langchain_core.callbacks import Callbacks
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import BaseGenerationOutputParser, BaseOutputParser
from langchain_core.runnables import Runnable, RunnableParallel
from pydantic import BaseModel

from ..model.abilities import is_json_mode_model, is_openai_function_model, is_vision_model
from ..model.defaults import univeral_model_selector
from ..parser.json_schema import RetryJsonPydanticParser
from ..parser.openai_functions import (
    RetryOpenAIFunctionPrimitiveTypeParser,
    RetryOpenAIFunctionPydanticParser,
    RetryOpenAIFunctionPydanticUnionParser,
)
from ..parser.primitive_types import RetryJsonPrimitiveTypeParser
from ..parser.schema_converter import pydantic_to_grammar
from ..parser.selector import parser_for
from ..schema.signature import Signature
from ..syntax.input_types import Image
from ..syntax.output_types import ParserBaseModel
from ..syntax.params import Depends
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
    output_types: list[type],
    instruction_prompt: HumanImageMessagePromptTemplate,
    system: str,
    memory: BaseChatMessageHistory,
    context: list[BaseMessage],
    llm: BaseChatModel,
    leading_runnable: Runnable[dict[str, Any], Any],
    input_kwargs: dict[str, Any],
) -> Runnable[dict[str, Any], Any]:
    """
    Compile a langchain runnable chain from the funcchain syntax.
    """
    if not all(issubclass(t, BaseModel) for t in output_types):
        raise RuntimeError("Funcchain union types are currently only supported for pydantic models.")

    output_type_names = [t.__name__ for t in output_types]

    input_kwargs["format_instructions"] = f"Extract to one of these output types: {output_type_names}."

    functions = multi_pydantic_to_functions(output_types)

    _llm = llm
    llm = _llm.bind(**functions)  # type: ignore

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

    return (
        leading_runnable
        | prompt
        | llm
        | RetryOpenAIFunctionPydanticUnionParser(output_types=output_types, retry=3, retry_llm=_llm)
    )


def patch_openai_function_to_pydantic(
    llm: BaseChatModel,
    output_type: type[BaseModel],
    input_kwargs: dict[str, Any],
    primitive_type: bool = False,
) -> tuple[BaseChatModel, BaseGenerationOutputParser]:
    input_kwargs["format_instructions"] = f"Extract to {output_type.__name__}."
    functions = pydantic_to_functions(output_type)

    _llm = llm
    llm = llm.bind(**functions)  # type: ignore

    if not primitive_type:
        return llm, RetryOpenAIFunctionPydanticParser(pydantic_schema=output_type, retry=3, retry_llm=_llm)
    return llm, RetryOpenAIFunctionPrimitiveTypeParser(pydantic_schema=output_type, retry=3, retry_llm=_llm)


def create_chain(
    system: str,
    instruction: str,
    output_types: list[type[ChainOutput]],
    context: list[BaseMessage],
    memory: BaseChatMessageHistory,
    settings: FuncchainSettings,
    input_args: list[tuple[str, type]],
    temp_images: list[Image] = [],
) -> Runnable[dict[str, Any], ChainOutput]:
    """
    Compile a langchain runnable chain from the funcchain syntax.
    """
    # large language model
    _llm = _gather_llm(settings)
    llm = _add_custom_callbacks(_llm, settings)

    parser = parser_for(output_types, retry=settings.retry_parse, llm=llm)

    # TODO collect types from input_args
    # -> this would allow special prompt templating based on certain types
    # -> e.g. BaseChatMessageHistory adds a history placeholder
    # -> e.g. BaseChatModel overrides the default language model
    # -> e.g. SettingsOverride overrides the default settings
    # -> e.g. Callbacks adds custom callbacks
    # -> e.g. SystemMessage adds a system message

    # handle input arguments
    prompt_args: list[str] = []
    pydantic_args: list[str] = []
    annotated_args: list[tuple[str, type]] = []
    special_args: list[tuple[str, type]] = []

    for i in input_args:
        if i[1] is str:
            prompt_args.append(i[0])
        elif get_origin(i[1]) is Annotated:
            annotated_args.append(i)
        elif issubclass(i[1], BaseModel):
            pydantic_args.append(i[0])
        else:
            special_args.append(i)

    dependencies: list[tuple[str, Depends]] = []

    for arg_name, arg_type in annotated_args:
        dependencies.append((arg_name, get_args(arg_type)[1:][0]))
        if get_args(arg_type)[0] is str:
            prompt_args.append(arg_name)

        if issubclass(get_args(arg_type)[0], BaseModel):
            pydantic_args.append(arg_name)

    leading_runnable: Runnable[Any, Any] = RunnableParallel(
        {
            **{name: itemgetter(name) for name in (prompt_args + pydantic_args)},
            **{name: dep.dependency for name, dep in dependencies},  # type: ignore
        }
    )

    # TODO: change this into input_args
    input_kwargs = {k: "" for k in (prompt_args + pydantic_args)}

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
    images.extend(temp_images)

    # create prompts
    instruction_prompt = create_instruction_prompt(
        instruction,
        images,
        input_kwargs,
        format_instructions=f_instructions,
    )
    chat_prompt = create_chat_prompt(system, instruction_prompt, context, memory)

    # TODO: think why this was needed
    # # add formatted instruction to chat history
    # memory.add_message(instruction_prompt.format(**input_kwargs))

    # if len(output_types) == 1:
    #     output_type: type[BaseModel] = output_types[0]
    #     try:
    #         structured_llm = llm.with_structured_output(output_type)
    #     except NotImplementedError:
    #         pass
    # elif len(output_types) > 1:
    #     # do special union type thing
    #     pass
    # else:
    #     structured_llm = None

    _inject_grammar_for_local_models(llm, output_types, parser)

    # function model patches
    if is_openai_function_model(llm):
        if len(output_types) > 1:
            return create_union_chain(
                output_types,
                instruction_prompt,
                system,
                memory,
                context,
                llm,
                leading_runnable,
                input_kwargs,
            )
        if isinstance(parser, RetryJsonPydanticParser) or isinstance(parser, RetryJsonPrimitiveTypeParser):
            output_type = parser.pydantic_object
            if issubclass(output_type, BaseModel) and not issubclass(output_type, ParserBaseModel):
                # openai json streaming
                if settings.streaming and hasattr(llm, "model_kwargs"):
                    llm.model_kwargs = {"response_format": {"type": "json_object"}}
                # primitive types
                elif isinstance(parser, RetryJsonPrimitiveTypeParser):
                    llm, parser = patch_openai_function_to_pydantic(llm, output_type, input_kwargs, primitive_type=True)
                # pydantic types
                else:
                    assert isinstance(parser, RetryJsonPydanticParser)
                    llm, parser = patch_openai_function_to_pydantic(llm, output_type, input_kwargs)
            # custom parsers
            elif issubclass(output_type, ParserBaseModel):
                # todo maybe add custom openai function parsing
                raise NotImplementedError("Custom parsers are not yet supported for function models.")

    if is_json_mode_model(llm):
        if len(output_types) > 1:
            # todo implement
            raise NotImplementedError("Union types are not yet supported for json mode models.")
        if isinstance(parser, RetryJsonPydanticParser) or isinstance(parser, RetryJsonPrimitiveTypeParser):
            output_type = parser.pydantic_object
            assert hasattr(llm, "model_kwargs")
            llm.model_kwargs = {"response_format": {"type": "json_object"}}

    assert parser is not None
    return leading_runnable | chat_prompt | llm | parser


def compile_chain(signature: Signature, temp_images: list[Image] = []) -> Runnable[dict[str, Any], ChainOutput]:
    """
    Compile a signature to a runnable chain.
    """
    system = (
        [msg for msg in signature.history if isinstance(msg, SystemMessage)] or [None]  # type: ignore
    )[0]

    from ..utils.memory import ChatMessageHistory

    memory = ChatMessageHistory(messages=signature.history)

    return create_chain(
        msg_to_str(system) if system else "",
        signature.instruction,
        signature.output_types,
        signature.history,
        memory,
        signature.settings,
        signature.input_args,
        temp_images,
    )


def _add_format_instructions(
    parser: BaseOutputParser,
    instruction: str,
    input_kwargs: dict[str, Any],
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
    input_kwargs: dict[str, Any],
) -> list[Image]:
    """
    Handle images for vision models.
    """
    images = [v for v in input_kwargs.values() if isinstance(v, Image)]
    if is_vision_model(llm):
        for k in list(input_kwargs.keys()):
            if isinstance(input_kwargs[k], Image):
                del input_kwargs[k]
    elif images:
        raise RuntimeError("Images as input are only supported for vision models.")
    elif _history_contains_images(memory):
        print("Warning: Images in chat history are ignored for non-vision models.")
        memory.messages = _clear_images_from_history(memory.messages)

    return images


def _inject_grammar_for_local_models(
    llm: BaseChatModel,
    output_types: list[type],
    parser: BaseOutputParser | BaseGenerationOutputParser,
) -> None:
    """
    Inject GBNF grammar into local models.
    """
    try:
        from funcchain.model.patches.ollama import ChatOllama
    except:  # noqa
        pass
    else:
        if isinstance(llm, ChatOllama):
            if len(output_types) > 1:
                raise NotImplementedError("Union types are not yet supported for LlamaCpp models.")  # TODO: implement
            output_type = output_types[0]
            if issubclass(output_type, BaseModel) and not issubclass(output_type, ParserBaseModel):
                assert isinstance(parser, RetryJsonPydanticParser)
                output_type = parser.pydantic_object
                llm.grammar = pydantic_to_grammar(output_type)
            if issubclass(output_type, ParserBaseModel):
                llm.grammar = output_type.custom_grammar()
    try:
        from llama_cpp import LlamaGrammar

        from ..model.patches.llamacpp import ChatLlamaCpp
    except:  # noqa
        pass
    else:
        if isinstance(llm, ChatLlamaCpp):
            if len(output_types) > 1:  # TODO: implement
                raise NotImplementedError("Union types are not yet supported for LlamaCpp models.")

            output_type = output_types[0]
            if isinstance(parser, RetryJsonPydanticParser) or isinstance(parser, RetryJsonPrimitiveTypeParser):
                output_type = parser.pydantic_object

                if issubclass(output_type, BaseModel) and not issubclass(output_type, ParserBaseModel):
                    assert isinstance(parser, RetryJsonPydanticParser)
                    output_type = parser.pydantic_object
                    grammar: str | None = pydantic_to_grammar(output_type)
                if issubclass(output_type, ParserBaseModel):
                    grammar = output_type.custom_grammar()
                if grammar:
                    setattr(
                        llm,
                        "grammar",
                        LlamaGrammar.from_string(grammar, verbose=False),
                    )


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
