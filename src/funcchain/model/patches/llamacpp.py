from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel, BaseLanguageModel
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    ChatMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.pydantic_v1 import Field, root_validator
from langchain_core.utils import get_pydantic_field_names
from langchain_core.utils.utils import build_extra_kwargs

logger = logging.getLogger(__name__)


try:

    class _LlamaCppCommon(BaseLanguageModel):
        client: Any = Field(default=None, exclude=True)  #: :meta private:
        model_path: str
        """The path to the Llama model file."""

        lora_base: Optional[str] = None
        """The path to the Llama LoRA base model."""

        lora_path: Optional[str] = None
        """The path to the Llama LoRA. If None, no LoRa is loaded."""

        n_ctx: int = Field(4096, alias="n_ctx")
        """Token context window."""

        n_parts: int = Field(-1, alias="n_parts")
        """Number of parts to split the model into.
        If -1, the number of parts is automatically determined."""

        seed: int = Field(-1, alias="seed")
        """Seed. If -1, a random seed is used."""

        f16_kv: bool = Field(True, alias="f16_kv")
        """Use half-precision for key/value cache."""

        logits_all: bool = Field(False, alias="logits_all")
        """Return logits for all tokens, not just the last token."""

        vocab_only: bool = Field(False, alias="vocab_only")
        """Only load the vocabulary, no weights."""

        use_mlock: bool = Field(False, alias="use_mlock")
        """Force system to keep model in RAM."""

        n_threads: Optional[int] = Field(None, alias="n_threads")
        """Number of threads to use.
        If None, the number of threads is automatically determined."""

        n_batch: Optional[int] = Field(8, alias="n_batch")
        """Number of tokens to process in parallel.
        Should be a number between 1 and n_ctx."""

        n_gpu_layers: Optional[int] = Field(42, alias="n_gpu_layers")
        """Number of layers to be loaded into gpu memory. Default 42."""

        suffix: Optional[str] = Field(None)
        """A suffix to append to the generated text. If None, no suffix is appended."""

        max_tokens: Optional[int] = 1024
        """The maximum number of tokens to generate."""

        temperature: Optional[float] = 0.3
        """The temperature to use for sampling."""

        top_p: Optional[float] = 0.95
        """The top-p value to use for sampling."""

        logprobs: Optional[int] = Field(None)
        """The number of logprobs to return. If None, no logprobs are returned."""

        echo: Optional[bool] = False
        """Whether to echo the prompt."""

        stop: Optional[List[str]] = []
        """A list of strings to stop generation when encountered."""

        repeat_penalty: Optional[float] = 1.1
        """The penalty to apply to repeated tokens."""

        top_k: Optional[int] = 40
        """The top-k value to use for sampling."""

        last_n_tokens_size: Optional[int] = 64
        """The number of tokens to look back when applying the repeat_penalty."""

        use_mmap: Optional[bool] = True
        """Whether to keep the model loaded in RAM"""

        rope_freq_scale: float = 1.0
        """Scale factor for rope sampling."""

        rope_freq_base: float = 10000.0
        """Base frequency for rope sampling."""

        model_kwargs: Dict[str, Any] = Field(default_factory=dict)
        """Any additional parameters to pass to llama_cpp.Llama."""

        streaming: bool = True
        """Whether to stream the results, token by token."""

        grammar_path: Optional[Union[str, Path]] = None
        """
        grammar_path: Path to the .gbnf file that defines formal grammars
        for constraining model outputs. For instance, the grammar can be used
        to force the model to generate valid JSON or to speak exclusively in emojis. At most
        one of grammar_path and grammar should be passed in.
        """
        grammar: Optional[str] = None
        """
        grammar: formal grammar for constraining model outputs. For instance, the grammar
        can be used to force the model to generate valid JSON or to speak exclusively in
        emojis. At most one of grammar_path and grammar should be passed in.
        """

        verbose: bool = False
        """Print verbose output to stderr."""

        @root_validator()
        def validate_environment(cls, values: Dict) -> Dict:
            """Validate that llama-cpp-python library is installed."""
            try:
                from llama_cpp import Llama, LlamaGrammar
            except ImportError:
                raise ImportError(
                    "Could not import llama-cpp-python library. "
                    "Please install the llama-cpp-python library to "
                    "use this embedding model: pip install llama-cpp-python"
                )

            model_path = values["model_path"]
            model_param_names = [
                "rope_freq_scale",
                "rope_freq_base",
                "lora_path",
                "lora_base",
                "n_ctx",
                "n_parts",
                "seed",
                "f16_kv",
                "logits_all",
                "vocab_only",
                "use_mlock",
                "n_threads",
                "n_batch",
                "use_mmap",
                "last_n_tokens_size",
                "verbose",
            ]
            model_params = {k: values[k] for k in model_param_names}
            # For backwards compatibility, only include if non-null.
            if values["n_gpu_layers"] is not None:
                model_params["n_gpu_layers"] = values["n_gpu_layers"]

            model_params.update(values["model_kwargs"])

            try:
                values["client"] = Llama(model_path, **model_params)
            except Exception as e:
                raise ValueError(f"Could not load Llama model from path: {model_path}. " f"Received error {e}")

            if values["grammar"] and values["grammar_path"]:
                grammar = values["grammar"]
                grammar_path = values["grammar_path"]
                raise ValueError(
                    "Can only pass in one of grammar and grammar_path. Received " f"{grammar=} and {grammar_path=}."
                )
            elif isinstance(values["grammar"], str):
                values["grammar"] = LlamaGrammar.from_string(values["grammar"])
            elif values["grammar_path"]:
                values["grammar"] = LlamaGrammar.from_file(values["grammar_path"])
            else:
                pass
            return values

        @root_validator(pre=True)
        def build_model_kwargs(cls, values: Dict[str, Any]) -> Dict[str, Any]:
            """Build extra kwargs from additional params that were passed in."""
            all_required_field_names = get_pydantic_field_names(cls)
            extra = values.get("model_kwargs", {})
            values["model_kwargs"] = build_extra_kwargs(extra, values, all_required_field_names)
            return values

        @property
        def _default_params(self) -> Dict[str, Any]:
            """Get the default parameters for calling llama_cpp."""
            params = {
                "suffix": self.suffix,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "logprobs": self.logprobs,
                "echo": self.echo,
                "stop_sequences": self.stop,  # key here is convention among LLM classes
                "repeat_penalty": self.repeat_penalty,
                "top_k": self.top_k,
            }
            if self.grammar:
                params["grammar"] = self.grammar
            return params

        @property
        def _identifying_params(self) -> Dict[str, Any]:
            """Get the identifying parameters."""
            return {**{"model_path": self.model_path}, **self._default_params}

        def _get_parameters(self, stop: Optional[List[str]] = None) -> Dict[str, Any]:
            """
            Performs sanity check, preparing parameters in format needed by llama_cpp.

            Args:
                stop (Optional[List[str]]): List of stop sequences for llama_cpp.

            Returns:
                Dictionary containing the combined parameters.
            """

            # Raise error if stop sequences are in both input and default params
            if self.stop and stop is not None:
                raise ValueError("`stop` found in both the input and default params.")

            params = self._default_params

            # llama_cpp expects the "stop" key not this, so we remove it:
            params.pop("stop_sequences")

            # then sets it as configured, or default to an empty list:
            params["stop"] = self.stop or stop or []

            return params

        def get_num_tokens(self, text: str) -> int:
            tokenized_text = self.client.tokenize(text.encode("utf-8"))
            return len(tokenized_text)

    class ChatLlamaCpp(BaseChatModel, _LlamaCppCommon):
        """llama.cpp chat model.

        To use, you should have the llama-cpp-python library installed, and provide the
        path to the Llama model as a named parameter to the constructor.
        Check out: https://github.com/abetlen/llama-cpp-python

        Example:
            .. code-block:: python

                from funcchain._llms import ChatLlamaCpp
                llm = ChatLlamaCpp(model_path="./path/to/model.gguf")
        """

        @property
        def _llm_type(self) -> str:
            """Return type of chat model."""
            return "llamacpp-chat"

        def _format_message_as_text(self, message: BaseMessage) -> str:
            if isinstance(message, ChatMessage):
                message_text = f"\n\n{message.role.capitalize()}: {message.content}"
            elif isinstance(message, HumanMessage):
                message_text = f"[INST] {message.content} [/INST]"
            elif isinstance(message, AIMessage):
                message_text = f"{message.content}"
            elif isinstance(message, SystemMessage):
                message_text = f"<<SYS>> {message.content} <</SYS>>"
            else:
                raise ValueError(f"Got unknown type {message}")
            return message_text

        def _format_messages_as_text(self, messages: List[BaseMessage]) -> str:
            return "\n".join([self._format_message_as_text(message) for message in messages])

        def _stream_with_aggregation(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            verbose: bool = False,
            **kwargs: Any,
        ) -> ChatGenerationChunk:
            final_chunk: Optional[ChatGenerationChunk] = None
            for chunk in self._stream(messages, stop, **kwargs):
                if final_chunk is None:
                    final_chunk = chunk
                else:
                    final_chunk += chunk
                if run_manager:
                    run_manager.on_llm_new_token(
                        chunk.text,
                        verbose=verbose,
                    )
            if final_chunk is None:
                raise ValueError("No data received from llamacpp stream.")

            return final_chunk

        def _generate(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
        ) -> ChatResult:
            """Call out to LlamaCpp's generation endpoint.

            Args:
                messages: The list of base messages to pass into the model.
                stop: Optional list of stop words to use when generating.

            Returns:
                Chat generations from the model

            Example:
                .. code-block:: python

                    response = llamacpp([
                        HumanMessage(content="Tell me about the history of AI")
                    ])
            """
            final_chunk = self._stream_with_aggregation(
                messages, stop=stop, run_manager=run_manager, verbose=self.verbose, **kwargs
            )
            chat_generation = ChatGeneration(
                message=AIMessage(content=final_chunk.text),
                generation_info=final_chunk.generation_info,
            )
            return ChatResult(generations=[chat_generation])

        def _stream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
        ) -> Iterator[ChatGenerationChunk]:
            params = {**self._get_parameters(stop), **kwargs}
            prompt = self._format_messages_as_text(messages)
            result = self.client(prompt=prompt, stream=True, **params)
            for part in result:
                logprobs = part["choices"][0].get("logprobs", None)
                chunk = ChatGenerationChunk(
                    message=AIMessageChunk(content=part["choices"][0]["text"]),
                    generation_info={"logprobs": logprobs},
                )
                yield chunk
                if run_manager:
                    run_manager.on_llm_new_token(token=chunk.text, verbose=self.verbose, log_probs=logprobs)
except ImportError:

    class ChatLlamaCpp:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ImportError("Please install langchain_community to use ChatLlamaCpp.")
