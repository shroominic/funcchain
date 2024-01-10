from typing import Any, Generic, TypeVar

from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage

from ..backend.settings import FuncchainSettings, settings

T = TypeVar("T", bound=Any)


class Signature(BaseModel, Generic[T]):
    """
    Fundamental structure of an executable prompt.
    """

    instruction: str
    """ Prompt instruction to the language model. """

    input_args: list[str] = Field(default_factory=list)
    """ List of input arguments for the prompt template. """

    output_type: type[T] = Field(default=str)
    """ Type to parse the output into. """

    # todo: should this be defined at compile time? maybe runtime is better
    llm: BaseChatModel | str
    """ Chat model to use as string or langchain object. """

    # todo: is history really needed? maybe this could be a background optimization
    history: list[BaseMessage] = Field(default_factory=list)
    """ Additional messages that are inserted before the instruction. """

    # update_history: bool = Field(default=True)

    settings: FuncchainSettings = Field(default=settings)
    """ Local settings to override global settings. """

    class Config:
        arbitrary_types_allowed = True

    def __hash__(self) -> int:
        """Hash for caching keys."""
        return hash(
            (
                self.instruction,
                tuple(self.input_args),
                self.output_type,
                self.llm,
                tuple(self.history),
                self.settings,
            )
        )
