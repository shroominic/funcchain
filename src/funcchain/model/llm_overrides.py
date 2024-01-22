from typing import Any, Dict, Optional

from langchain_core.pydantic_v1 import validator

try:
    from langchain_community.chat_models import ChatOllama as _ChatOllama

    class ChatOllama(_ChatOllama):  # type: ignore
        grammar: Optional[str] = None
        """
        The [GBNF](https://github.com/ggerganov/llama.cpp/tree/master/grammars) grammar used to constrain the output.
        """

        @validator("grammar")
        def _validate_grammar(cls, v: Optional[str]) -> Optional[str]:
            if v is not None and "root ::=" not in v:
                raise ValueError("Grammar must contain a root rule.")
            return v

        @property
        def _default_params(self) -> Dict[str, Any]:
            """Get the default parameters for calling Ollama."""
            return {
                "model": self.model,
                "format": self.format,
                "options": {
                    "mirostat": self.mirostat,
                    "mirostat_eta": self.mirostat_eta,
                    "mirostat_tau": self.mirostat_tau,
                    "num_ctx": self.num_ctx,
                    "num_gpu": self.num_gpu,
                    "num_thread": self.num_thread,
                    "repeat_last_n": self.repeat_last_n,
                    "repeat_penalty": self.repeat_penalty,
                    "temperature": self.temperature,
                    "stop": self.stop,
                    "tfs_z": self.tfs_z,
                    "top_k": self.top_k,
                    "top_p": self.top_p,
                    "grammar": self.grammar,  # added
                },
                "system": self.system,
                "template": self.template,
            }


except ImportError:

    class ChatOllama:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ImportError("Please install langchain_community to use ChatOllama.")
