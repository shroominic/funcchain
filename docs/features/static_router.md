<!-- markdownlint-disable MD033 MD046 -->
# Static Routing with Funcchain and Pydantic

!!! Example
    See [static_router.py](https://github.com/shroominic/funcchain/blob/main/examples/static_router.py)

    This serves as an example of how to implement static routing using funcchain for decision-making and Enum for route selection.
    This is a useful task for applications that need to route user requests to specific handlers based on the content of the request.
    You can adapt this for your own usage.

## Full Code Example

<pre><code id="codeblock">
```python
from enum import Enum
from typing import Any

from funcchain import chain, settings
from pydantic import BaseModel, Field

settings.console_stream = True

def handle_pdf_requests(user_query: str) -> None:
    print("Handling PDF requests with user query: ", user_query)

def handle_csv_requests(user_query: str) -> None:
    print("Handling CSV requests with user query: ", user_query)

def handle_default_requests(user_query: str) -> Any:
    print("Handling DEFAULT requests with user query: ", user_query)

class RouteChoices(str, Enum):
    pdf = "pdf"
    csv = "csv"
    default = "default"

class Router(BaseModel):
    selector: RouteChoices = Field(description="Enum of the available routes.")

    def invoke_route(self, user_query: str) -> Any:
        match self.selector.value:
            case RouteChoices.pdf:
                return handle_pdf_requests(user_query)
            case RouteChoices.csv:
                return handle_csv_requests(user_query)
            case RouteChoices.default:
                return handle_default_requests(user_query)

def route_query(user_query: str) -> Router:
    return chain()

user_query = input("Enter your query: ")
routed_chain = route_query(user_query)
routed_chain.invoke_route(user_query)
```
</code></pre>

Demo

<div class="termy">

    ```python
    Enter your query:
    $ I need to process a CSV file

    Handling CSV requests with user query: I need to process a CSV file
    ```
</div>

## Instructions

!!! Step-by-Step
    We will implement a script with the functionality to take a user query, determine the type of request (PDF, CSV, or default), and invoke the appropriate handler function.

    **Necessary Imports**

    ```python
    from enum import Enum
    from typing import Any
    from funcchain import chain, settings
    from pydantic import BaseModel, Field
    ```

    **Define Route Handlers**

    These functions are the specific handlers for different types of user queries.

    ```python
    def handle_pdf_requests(user_query: str) -> None:
        print("Handling PDF requests with user query: ", user_query)

    def handle_csv_requests(user_query: str) -> None:
        print("Handling CSV requests with user query: ", user_query)

    def handle_default_requests(user_query: str) -> Any:
        print("Handling DEFAULT requests with user query: ", user_query)
    ```

    **Create RouteChoices Enum and Router Model**

    RouteChoices is an Enum that defines the possible routes. Router is a Pydantic model that selects and invokes the appropriate handler based on the route.

    ```python
    class RouteChoices(str, Enum):
        pdf = "pdf"
        csv = "csv"
        default = "default"

    class Router(BaseModel):
        selector: RouteChoices = Field(description="Enum of the available routes.")

        def invoke_route(self, user_query: str) -> Any:
            match self.selector.value:
                case RouteChoices.pdf:
                    return handle_pdf_requests(user_query)
                case RouteChoices.csv:
                    return handle_csv_requests(user_query)
                case RouteChoices.default:
                    return handle_default_requests(user_query)
    ```

    **Implement Routing Logic**

    The route_query function is intended to determine the best route for a given user query using the `chain()` function.

    ```python
    def route_query(user_query: str) -> Router:
        return chain()
    ```

    **Execute the Routing System**

    This block runs the routing system, asking the user for a query and then processing it through the defined routing logic.

    ```python
    user_query = input("Enter your query: ")
    routed_chain = route_query(user_query)
    routed_chain.invoke_route(user_query)
    ```
