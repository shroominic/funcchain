from typing import Any

from langchain_core.messages import BaseMessage
from langchain_core.pydantic_v1 import BaseModel, Field

from ..backend.settings import FuncchainSettings, settings


class Signature(BaseModel):
    """
    Fundamental structure of an executable prompt.
    """

    instruction: str
    """ Prompt instruction to the language model. """

    input_args: list[tuple[str, Any]] = Field(default_factory=list)
    """ List of input arguments for the prompt template. """

    output_types: list[Any]
    """ Type to parse the output into. """

    # todo: is history really needed? maybe this could be a background optimization
    history: list[BaseMessage] = Field(default_factory=list)
    """ Additional messages that are inserted before the instruction. """

    # update_history: bool = Field(default=True)

    # todo: should this be defined at compile time? maybe runtime is better
    settings: FuncchainSettings = Field(default=settings)
    """ Local settings to override global settings. """

    # auto_tune: bool = Field(default=False)
    # """ Whether to auto tune the prompt using dspy. """

    class Config:
        arbitrary_types_allowed = True

    def __hash__(self) -> int:
        """Hash for caching keys."""
        return hash(
            (
                self.instruction,
                tuple(self.input_args),
                tuple(self.output_types),
                tuple(self.history),
                self.settings,
            )
        )
