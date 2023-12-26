from enum import Enum
from typing import Iterator, Union, Callable, Any, TypeVar, Optional, AsyncIterator
from typing_extensions import TypedDict
from langchain_core.pydantic_v1 import validator as field_validator
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable, RunnableConfig, RunnableSerializable
from funcchain import runnable
from .utils.msg_tools import msg_to_str


class Route(TypedDict):
    handler: Callable
    description: str


Routes = dict[str, Union[Route, Callable]]

ResponseType = TypeVar("ResponseType")


class ChatRouter(RunnableSerializable[HumanMessage, ResponseType]):
    routes: Routes
    history: BaseChatMessageHistory | None = None
    llm: BaseChatModel | str | None = None

    class Config:
        arbitrary_types_allowed = True

    @field_validator("routes")
    def validate_routes(cls, v: Routes) -> Routes:
        if "default" not in v.keys():
            raise ValueError("`default` route is missing")
        return v

    def create_route(self) -> Runnable[dict[str, str], Any]:
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

        return runnable(
            instruction="Given the user request select the appropriate route.",
            input_args=["user_request", "routes"],  # todo: optional image
            output_type=RouterModel,
            context=self.history.messages if self.history else [],
            settings_override={"llm": self.llm},
        )

    def show_routes(self) -> str:
        return "\n".join(
            [
                f"{route_name}: {route['description']}"
                if isinstance(route, dict)
                else f"{route_name}: {route.__name__}"
                for route_name, route in self.routes.items()
            ]
        )

    def invoke_route(self, user_query: str, /, **kwargs: Any) -> ResponseType:
        route_query = self.create_route()

        selected_route = route_query.invoke(
            input={
                "user_request": user_query,
                "routes": self.show_routes(),
            },
            config={"run_name": "ChatRouter"},
        ).selector
        assert isinstance(selected_route, str)

        if isinstance(self.routes[selected_route], dict):
            return self.routes[selected_route]["handler"](user_query, **kwargs)  # type: ignore
        return self.routes[selected_route](user_query, **kwargs)  # type: ignore

    async def ainvoke_route(self, user_query: str, /, **kwargs: Any) -> Any:
        import asyncio

        if not all(
            [
                asyncio.iscoroutinefunction(route["handler"])
                if isinstance(route, dict)
                else asyncio.iscoroutinefunction(route)
                for route in self.routes.values()
            ]
        ):
            raise ValueError("All routes must be awaitable when using `ainvoke_route`")

        route_query = self.create_route()
        selected_route = route_query.invoke(
            input={
                "user_request": user_query,
                "routes": self.show_routes(),
            },
            config={"run_name": "ChatRouter"},
        ).selector
        assert isinstance(selected_route, str)

        if isinstance(self.routes[selected_route], dict):
            return await self.routes[selected_route]["handler"](user_query, **kwargs)  # type: ignore
        return await self.routes[selected_route](user_query, **kwargs)  # type: ignore

    def invoke(
        self,
        input: HumanMessage,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> ResponseType:
        user_query = msg_to_str(input)
        route_query = self.create_route()

        selected_route = route_query.invoke(
            input={
                "user_request": user_query,
                "routes": self.show_routes(),
            },
            config=config.update({"run_name": "ChatRouter"}) if config else None,
        ).selector
        assert isinstance(selected_route, str)

        if isinstance(self.routes[selected_route], dict):
            if hasattr(self.routes[selected_route]["handler"], "invoke"):  # type: ignore
                return self.routes[selected_route]["handler"].invoke(  # type: ignore
                    input, config, **kwargs
                )
            return self.routes[selected_route]["handler"](user_query, **kwargs)  # type: ignore

        if hasattr(self.routes[selected_route], "invoke"):
            return self.routes[selected_route].invoke(input, config, **kwargs)  # type: ignore
        return self.routes[selected_route](user_query, **kwargs)  # type: ignore

    async def ainvoke(
        self,
        input: HumanMessage,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> ResponseType:
        user_query = msg_to_str(input)
        import asyncio

        if not all(
            [
                asyncio.iscoroutinefunction(route["handler"])
                if isinstance(route, dict)
                else asyncio.iscoroutinefunction(route)
                for route in self.routes.values()
            ]
        ):
            raise ValueError("All routes must be awaitable when using `ainvoke_route`")

        route_query = self.create_route()
        selected_route = route_query.invoke(
            input={
                "user_request": user_query,
                "routes": self.show_routes(),
            },
            config=config.update({"run_name": "ChatRouter"}) if config else None,
        ).selector
        assert isinstance(selected_route, str)

        if isinstance(self.routes[selected_route], dict):
            if hasattr(self.routes[selected_route]["handler"], "ainvoke"):  # type: ignore
                return await self.routes[selected_route]["handler"].ainvoke(  # type: ignore
                    input, config, **kwargs
                )
            return await self.routes[selected_route]["handler"](user_query, **kwargs)  # type: ignore

        if hasattr(self.routes[selected_route], "ainvoke"):
            return await self.routes[selected_route].ainvoke(input, config, **kwargs)  # type: ignore
        return await self.routes[selected_route](user_query, **kwargs)  # type: ignore

    def stream(
        self,
        input: HumanMessage,
        config: RunnableConfig | None = None,
        **kwargs: Any | None,
    ) -> Iterator[ResponseType]:
        user_query = msg_to_str(input)
        route_query = self.create_route()

        selected_route = route_query.invoke(
            input={
                "user_request": user_query,
                "routes": self.show_routes(),
            },
            config=config.update({"run_name": "ChatRouter"}) if config else None,
        ).selector
        assert isinstance(selected_route, str)

        if isinstance(self.routes[selected_route], dict):
            if hasattr(self.routes[selected_route]["handler"], "stream"):  # type: ignore
                yield from self.routes[selected_route]["handler"].stream(  # type: ignore
                    input, config, **kwargs
                )
            yield self.routes[selected_route]["handler"](user_query, **kwargs)  # type: ignore

        if hasattr(self.routes[selected_route], "stream"):
            yield from self.routes[selected_route].stream(input, config, **kwargs)  # type: ignore
        yield self.routes[selected_route](user_query, **kwargs)  # type: ignore

    async def astream(
        self,
        input: HumanMessage,
        config: RunnableConfig | None = None,
        **kwargs: Any | None,
    ) -> AsyncIterator[ResponseType]:
        user_query = msg_to_str(input)
        import asyncio

        if not all(
            [
                asyncio.iscoroutinefunction(route["handler"])
                if isinstance(route, dict)
                else asyncio.iscoroutinefunction(route)
                for route in self.routes.values()
            ]
        ):
            raise ValueError("All routes must be awaitable when using `ainvoke_route`")

        route_query = self.create_route()
        selected_route = (
            await route_query.ainvoke(
                input={
                    "user_request": user_query,
                    "routes": self.show_routes(),
                },
                config=config.update({"run_name": "ChatRouter"}) if config else None,
            )
        ).selector
        assert isinstance(selected_route, str)

        if isinstance(self.routes[selected_route], dict):
            if hasattr(self.routes[selected_route]["handler"], "astream"):  # type: ignore
                async for item in self.routes[selected_route]["handler"].astream(  # type: ignore
                    input, config, **kwargs
                ):
                    yield item
            yield await self.routes[selected_route]["handler"](user_query, **kwargs)  # type: ignore

        if hasattr(self.routes[selected_route], "astream"):
            async for item in self.routes[selected_route].astream(  # type: ignore
                input, config, **kwargs
            ):
                yield item
        yield await self.routes[selected_route](user_query, **kwargs)  # type: ignore
