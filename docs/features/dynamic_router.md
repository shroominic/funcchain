<!-- markdownlint-disable MD033 MD046 -->
# Dynamic Chat Router with Funcchain

!!! Example
    dynamic_router.py [Example](https://github.com/shroominic/funcchain/blob/main/examples/dynamic_router.py)

In this example we will use funcchain to build a LLM routing pipeline.
This is a very useful LLM task and can be used in a variety of applications.
You can abstract this for your own usage.
This should serve as an example of how to archive complex structures using funcchain.

A dynamic chat router that selects the appropriate handler for user queries based on predefined routes.

## Full Code Example

```python
from enum import Enum
from typing import Any, Callable, TypedDict

from funcchain.syntax.executable import compile_runnable
from pydantic import BaseModel, Field


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
            output_type=RouterModel,
        )

        selected_route = route_query.invoke(
            input={
                "user_query": user_query,
                "query_handlers": self._routes_repr(),
            }
        ).selector
        assert isinstance(selected_route, str)

        return self.routes[selected_route]["handler"](user_query, **kwargs)


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
```

## Demo

<div class="termy">
    ```python
    $ router.invoke_route("Can you summarize this csv?")
    Handling CSV requests with user query: Can you summarize this csv?
    ```
</div>

## Instructions

!!! Step-by-Step

    **Nececary imports**

    ```python
    from enum import Enum
    from typing import Any, Callable, TypedDict

    from funcchain.syntax.executable import compile_runnable
    from pydantic import BaseModel, Field
    ```

    **Define Route Type**

    ```python
    class Route(TypedDict):
        handler: Callable
        description: str
    ```

    Create a `TypedDict` to define the structure of a route with a handler function and a description. Just leave this unchanged if not intentionally experimenting.

    **Implement Route Representation**

    Establish a Router class

    ```python
    class DynamicChatRouter(BaseModel):
        routes: dict[str, Route]
    ```

    **_routes_repr():**

    Returns a string representation of all routes and their descriptions, used to help the language model understand the available routes.

    ```python
    def _routes_repr(self) -> str:
        return "\n".join([f"{route_name}: {route['description']}" for route_name, route in self.routes.items()])
    ```

    **invoke_route(user_query: str, **kwargs: Any) -> Any: **

    This method takes a user query and additional keyword arguments. Inside invoke_route, an Enum named RouteChoices is dynamically created with keys corresponding to the route names. This Enum is used to validate the selected route.

    ```python
    def invoke_route(self, user_query: str, /, **kwargs: Any) -> Any:
        RouteChoices = Enum(  # type: ignore
            "RouteChoices",
            {r: r for r in self.routes.keys()},
            type=str,
        )
    ```

    **Compile the Route Selection Logic**

    The `RouterModel` class in this example is used for defining the expected output structure that the `compile_runnable` function will use to determine the best route for a given user query.


    ```python
    class RouterModel(BaseModel):
        selector: RouteChoices = Field(
            default="default",
            description="Enum of the available routes.",
        )

    route_query = compile_runnable(
        instruction="Given the user query select the best query handler for it.",
        input_args=["user_query", "query_handlers"],
        output_type=RouterModel,
    )

    selected_route = route_query.invoke(
        input={
            "user_query": user_query,
            "query_handlers": self._routes_repr(),
        }
    ).selector
    assert isinstance(selected_route, str)

    return self.routes[selected_route]["handler"](user_query, **kwargs)
    ```

    - `RouterModel`: Holds the route selection with a default option, ready for you to play around with.
    - `RouteChoices`: An Enum built from route names, ensuring you only get valid route selections.
    - `compile_runnable`: Sets up the decision-making logic for route selection, guided by the provided instruction and inputs.
    - `route_query`: Calls the decision logic with the user's query and a string of route descriptions.
    - `selected_route`: The outcome of the decision logic, representing the route to take.
    - `assert`: A safety check to confirm the route is a string, as expected by the routes dictionary.
    - `handler invocation`: Runs the chosen route's handler with the provided query and additional arguments.

    **Define route functions**

    Now you can use the structured output to execute programatically based on a natural language input.
    Establish functions tailored to your needs.

    ```python
    def handle_pdf_requests(user_query: str) -> str:
    return "Handling PDF requests with user query: " + user_query

    def handle_csv_requests(user_query: str) -> str:
        return "Handling CSV requests with user query: " + user_query

    def handle_default_requests(user_query: str) -> str:
        return "Handling DEFAULT requests with user query: " + user_query
    ```

    **Define the routes**

    And bind the previous established functions.

    ```python
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
    ```

    **Get output**

    Use the router.invoke_route method to process the user query and obtain the appropriate response.

    ```python
    router.invoke_route("Can you summarize this csv?")
    ```
