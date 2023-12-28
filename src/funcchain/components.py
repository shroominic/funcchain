from enum import Enum
from typing import AsyncIterator, Callable, Any, Iterator, TypeVar, Optional
from typing_extensions import TypedDict
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import (
    Runnable,
    RunnableSerializable,
    RouterRunnable,
    RunnableLambda,
)
from langchain_core.runnables.config import RunnableConfig
from langchain_core.runnables.router import RouterInput
from funcchain import runnable
from funcchain.utils.msg_tools import msg_to_str


class Route(TypedDict):
    handler: Callable | Runnable
    description: str


Routes = dict[str, Route]

ResponseType = TypeVar("ResponseType")


class ChatRouter(RouterRunnable[ResponseType]):
    """A router component that can be used to route user requests to different handlers."""

    def __init__(
        self,
        *,
        routes: Routes,
        history: Optional[BaseChatMessageHistory] = None,
        llm: Optional[BaseChatModel | str] = None,
        add_default: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            runnables={name: run["handler"] for name, run in routes.items()},
            **kwargs,
        )
        self.llm = llm
        self.history = history
        self.routes = self._add_default_handler(routes) if add_default else routes

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"

    @classmethod
    def create_router(
        cls,
        *,
        routes: Routes,
        history: Optional[BaseChatMessageHistory] = None,
        llm: Optional[BaseChatModel | str] = None,
        **kwargs: Any,
    ) -> RunnableSerializable[Any, ResponseType]:
        router = cls(
            routes=routes, llm=llm, history=history, add_default=True, **kwargs
        )
        return {
            "input": lambda x: x,
            "key": (
                lambda x: {
                    # "image": x.images[0],
                    # "user_request": x.__str__(),
                    "user_request": x.content,
                    "routes": router._routes_repr(),
                }
            )
            | cls._selector(routes, llm, history)
            | RunnableLambda(lambda x: x.selector.__str__()),
        } | router

    @staticmethod
    def _selector(
        routes: Routes,
        llm: BaseChatModel | str | None = None,
        history: BaseChatMessageHistory | None = None,
    ) -> Runnable[dict[str, str], Any]:
        RouteChoices = Enum(  # type: ignore
            "RouteChoices",
            {r: r for r in routes.keys()},
            type=str,
        )
        from pydantic import BaseModel, Field

        class RouterModel(BaseModel):
            selector: RouteChoices = Field(
                default="default",
                description="Enum of the available routes.",
            )

        return runnable(
            instruction="Given the user request select the appropriate route.",
            input_args=["user_request", "routes"],  # todo: optional images
            output_type=RouterModel,
            context=history.messages if history else [],
            settings_override={"llm": llm},
        )

    def _add_default_handler(self, routes: Routes) -> Routes:
        if "default" not in routes.keys():
            routes["default"] = {
                "handler": (
                    RunnableLambda(lambda x: msg_to_str(x))
                    | runnable(
                        instruction="{user_request}",
                        input_args=["user_request"],
                        output_type=str,
                        settings_override={"llm": self.llm},
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
        return routes

    def _routes_repr(self) -> str:
        return "\n".join(
            [
                f"{route_name}: {route['description']}"
                for route_name, route in self.routes.items()
            ]
        )

    def post_update_history(self, input: RouterInput, output: ResponseType) -> None:
        input = input["input"]
        if self.history:
            if isinstance(input, HumanMessage):
                self.history.add_message(input)
            if isinstance(output, AIMessage):
                self.history.add_message(output)

    # TODO: deprecate
    def invoke_route(self, user_query: str, /, **kwargs: Any) -> ResponseType:
        """Deprecated. Use invoke instead."""
        route_query = self._selector(self.routes)

        selected_route = route_query.invoke(
            input={"user_request": user_query, "routes": self._routes_repr()}
        ).selector
        return self.routes[selected_route]["handler"](user_query, **kwargs)  # type: ignore

    def invoke(
        self, input: RouterInput, config: RunnableConfig | None = None
    ) -> ResponseType:
        output = super().invoke(input, config)
        self.post_update_history(input, output)
        return output

    async def ainvoke(
        self,
        input: RouterInput,
        config: RunnableConfig | None = None,
        **kwargs: Any | None,
    ) -> ResponseType:
        output = await super().ainvoke(input, config, **kwargs)
        self.post_update_history(input, output)
        return output

    def stream(
        self,
        input: RouterInput,
        config: RunnableConfig | None = None,
        **kwargs: Any | None,
    ) -> Iterator[ResponseType]:
        for i in super().stream(input, config, **kwargs):
            yield (last := i)
        if last:
            self.post_update_history(input, last)

    async def astream(
        self,
        input: RouterInput,
        config: RunnableConfig | None = None,
        **kwargs: Any | None,
    ) -> AsyncIterator[ResponseType]:
        async for ai in super().astream(input, config, **kwargs):
            yield (last := ai)
        if last:
            self.post_update_history(input, last)
