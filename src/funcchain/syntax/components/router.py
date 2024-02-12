from enum import Enum
from typing import Any, AsyncIterator, Callable, Iterator, Optional

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import (
    RouterRunnable,
    Runnable,
    RunnableConfig,
    RunnableLambda,
    RunnablePassthrough,
    RunnableSerializable,
)
from typing_extensions import TypedDict

from ...utils.msg_tools import msg_to_str
from ..executable import compile_runnable


class Route(TypedDict):
    handler: Callable | Runnable
    description: str


Routes = dict[str, Route]


class RouterChat(Runnable[HumanMessage, AIMessage]):
    """
    A router component that can be used to route user requests to different handlers.
    """

    def __init__(
        self,
        routes: Routes,
        llm: Optional[BaseChatModel | str] = None,
        history: Optional[BaseChatMessageHistory] = None,
        add_default_handler: bool = True,
    ) -> None:
        self.routes = routes
        self.llm = llm
        self.history = history

        if add_default_handler:
            self._add_default_handler()

    @property
    def runnable(self) -> RunnableSerializable[HumanMessage, AIMessage]:
        # TODO: update history somewhere
        return {
            "input": RunnablePassthrough(),
            "key": {
                # todo "images": x.images,
                "user_request": msg_to_str,
                "routes": lambda _: self._routes_repr(),
            }
            # route selection
            | self._selector()
            | (lambda x: x.selector.value),
        } | RouterRunnable(
            runnables={name: run["handler"] for name, run in self.routes.items()},
        )  # maybe add auto conversion of strings to AI Messages/Chunks

    def _selector(self) -> Runnable[dict[str, Any], Any]:
        RouteChoices = Enum(  # type: ignore
            "RouteChoices",
            {r: r for r in self.routes.keys()},
            type=str,
        )
        from pydantic import BaseModel, Field

        class RouterModel(BaseModel):
            selector: RouteChoices = Field(
                default="default",
                description="Enum of the available routes.",
            )

        return compile_runnable(
            instruction="Given the user request select the appropriate route.",
            input_args=["user_request", "routes"],  # todo: optional images
            output_types=[RouterModel],
            context=self.history.messages if self.history else [],
            llm=self.llm,
        )

    def _add_default_handler(self) -> None:
        if "default" not in self.routes.keys():
            self.routes["default"] = {
                "handler": (
                    {"user_request": lambda x: msg_to_str(x)}
                    | compile_runnable(
                        instruction="{user_request}",
                        input_args=["user_request"],
                        output_types=[str],
                        llm=self.llm,
                    )
                    | RunnableLambda(lambda x: AIMessage(content=x))
                ),
                "description": (
                    "Choose this for everything else like "
                    "normal questions or random things.\n"
                    "As example: 'How does this work?' or "
                    "'Whatsup' or 'What is the meaning of life?'"
                ),
            }

    def _routes_repr(self) -> str:
        return "\n".join([f"{route_name}: {route['description']}" for route_name, route in self.routes.items()])

    def invoke(self, input: HumanMessage, config: RunnableConfig | None = None) -> AIMessage:
        return self.runnable.invoke(input, config=config)

    async def ainvoke(self, input: HumanMessage, config: RunnableConfig | None = None, **kwargs: Any) -> AIMessage:
        return await self.runnable.ainvoke(input, config, **kwargs)

    def stream(
        self,
        input: HumanMessage,
        config: RunnableConfig | None = None,
        **kwargs: Any | None,
    ) -> Iterator[AIMessage]:
        yield from self.runnable.stream(input, config, **kwargs)

    async def astream(
        self,
        input: HumanMessage,
        config: RunnableConfig | None = None,
        **kwargs: Any | None,
    ) -> AsyncIterator[AIMessage]:
        async for msg in self.runnable.astream(input, config, **kwargs):
            yield msg
