from enum import Enum
from typing import Any, Callable, TypedDict

from funcchain.syntax.executable import compile_runnable
from pydantic import BaseModel, Field

# Dynamic Router Definition:


class Route(TypedDict):
    handler: Callable
    description: str


class DynamicChatRouter(BaseModel):
    routes: dict[str, Route]

    def _routes_repr(self) -> str:
        return "\n".join([f"{route_name}: {route['description']}" for route_name, route in self.routes.items()])

    def invoke_route(self, user_query: str, /, **kwargs: Any) -> Any:
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

        route_query = compile_runnable(
            instruction="Given the user query select the best query handler for it.",
            input_args=["user_query", "query_handlers"],
            output_types=[RouterModel],
        )

        selected_route = route_query.invoke(
            input={
                "user_query": user_query,
                "query_handlers": self._routes_repr(),
            }
        ).selector
        assert isinstance(selected_route, str)

        return self.routes[selected_route]["handler"](user_query, **kwargs)


# Example Usage:


def handle_pdf_requests(user_query: str) -> str:
    return "Handling PDF requests with user query: " + user_query


def handle_csv_requests(user_query: str) -> str:
    return "Handling CSV requests with user query: " + user_query


def handle_default_requests(user_query: str) -> str:
    return "Handling DEFAULT requests with user query: " + user_query


router = DynamicChatRouter(
    routes={
        "pdf": {
            "handler": handle_pdf_requests,
            "description": "Call this for requests including PDF Files.",
        },
        "csv": {
            "handler": handle_csv_requests,
            "description": "Call this for requests including CSV Files.",
        },
        "default": {
            "handler": handle_default_requests,
            "description": "Call this for all other requests.",
        },
    },
)


router.invoke_route("Can you summarize this csv?")
