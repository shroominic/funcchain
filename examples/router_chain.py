from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from funcchain import chain


def handle_pdf_requests(user_query: str) -> None:
    print("Handling pdf requests with user query: ", user_query)


def handle_csv_requests(user_query: str) -> None:
    print("Handling csv requests with user query: ", user_query)


def handle_normal_answer_requests(user_query: str) -> Any:
    print("Handling normal answer requests with user query: ", user_query)


class Routes(str, Enum):
    pdf = "pdf"
    csv = "csv"
    normal_answer = "normal_answer"

    def __call__(self, user_query: str) -> Any:
        match self.value:
            case self.pdf:
                return handle_pdf_requests(user_query)
            case self.csv:
                return handle_csv_requests(user_query)
            case self.normal_answer:
                return handle_normal_answer_requests(user_query)


class Router(BaseModel):
    selector: Routes = Field(description="Enum of the available routes.")


def route_query(user_query: str) -> Router:
    """
    Given a user query select the best query handler for it.
    """
    return chain()


if __name__ == "__main__":
    user_query = input("Enter your query: ")

    routed_chain = route_query(user_query)

    routed_chain.selector(user_query)
