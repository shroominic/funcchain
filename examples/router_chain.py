from typing import Any
from funcchain import chain, settings
from langchain.pydantic_v1 import BaseModel, Field, validator


settings.OPENAI_API_KEY = "sk-*******"


def handle_pdf_requests() -> None:
    print("Handling pdf requests")
    
def handle_csv_requests() -> None:
    print("Handling csv requests")
    
def handle_normal_answer_requests() -> Any:
    print("Handling normal answer requests")


ROUTES = {
    "pdf": handle_pdf_requests,
    "csv": handle_csv_requests,
    "normal answer": handle_normal_answer_requests,
}


class Route(BaseModel):
    selector: str = Field(..., description=f"Select one of the following options {ROUTES.keys()}")

    @validator("selector")
    def validate_selector(cls, v):
        if v not in ROUTES.keys():
            raise ValueError("Invalid selector")
        return v
    
    def __call__(self, *args, **kwargs) -> Any:
        return ROUTES[self.selector](*args, **kwargs)


def route_query(user_query: str, routes: str) -> Route:
    """
    USER_QUERY:
    {user_query}
    
    AVAILABLE ROUTES:
    {routes}

    Given a user query select the best query handler for it.
    """
    return chain()


if __name__ == "__main__":
    user_query = input("Enter your query: ")
    
    routed_chain = route_query(user_query, ROUTES.keys())
    
    routed_chain()
