from enum import Enum
from typing import Union, Callable, TypedDict, Any, Coroutine
from pydantic import BaseModel, Field, field_validator
from funcchain import runnable


class Route(TypedDict):
    handler: Union[Callable, Coroutine]
    description: str


Routes = dict[str, Union[Route, Callable, Coroutine]]


class ChatRouter(BaseModel):
    routes: Routes

    class Config:
        arbitrary_types_allowed = True

    @field_validator("routes")
    def validate_routes(cls, v: Routes) -> Routes:
        if "default" not in v.keys():
            raise ValueError("`default` route is missing")
        return v

    def create_route(self) -> Any:
        RouteChoices = Enum(  # type: ignore
            "RouteChoices",
            {r: r for r in self.routes.keys()},
            type=str,
        )

        class RouterModel(BaseModel):
            selector: RouteChoices = Field(
                default="default",
                description="Enum of the available routes.",
            )

        return runnable(
            instruction="Given the user query select the best query handler for it.",
            input_args=["user_query", "query_handlers"],
            output_type=RouterModel,
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

    def invoke_route(self, user_query: str, /, **kwargs: Any) -> Any:
        route_query = self.create_route()

        selected_route = route_query.invoke(
            input={
                "user_query": user_query,
                "query_handlers": self.show_routes(),
            }
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
                "user_query": user_query,
                "query_handlers": self.show_routes(),
            }
        ).selector
        assert isinstance(selected_route, str)

        if isinstance(self.routes[selected_route], dict):
            return await self.routes[selected_route]["handler"](user_query, **kwargs)  # type: ignore
        return await self.routes[selected_route](user_query, **kwargs)  # type: ignore
