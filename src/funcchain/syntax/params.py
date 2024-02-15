from typing import Any, Optional

from langchain_core.runnables.base import RunnableLike


class Depends:
    def __init__(
        self,
        dependency: Optional[RunnableLike[Any, Any]] = None,
    ):
        self.dependency = dependency

    def __repr__(self) -> str:
        return str(self.__class__.__name__) + str(
            getattr(
                self.dependency,
                "__name__",
                type(self.dependency).__name__,
            )
        )
