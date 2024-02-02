from enum import Enum
from typing import Any

from funcchain import chain, settings
from pydantic import BaseModel, Field

settings.console_stream = True
# settings.llm = "ollama/openhermes2.5-mistral"


def handle_pdf_requests(
    user_query: str,
) -> None:
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
    """
    Given a user query select the best query handler for it.
    """
    return chain()


if __name__ == "__main__":
    user_query = input("Enter your query: ")

    routed_chain = route_query(user_query)

    routed_chain.invoke_route(user_query)
