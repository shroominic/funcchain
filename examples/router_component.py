from funcchain.components import ChatRouter
from funcchain.settings import settings

settings.llm = "ollama/openchat"


def handle_pdf_requests(user_query: str) -> str:
    return "Handling PDF requests with user query: " + user_query


def handle_csv_requests(user_query: str) -> str:
    return "Handling CSV requests with user query: " + user_query


def handle_default_requests(user_query: str) -> str:
    return "Handling DEFAULT requests with user query: " + user_query


router = ChatRouter[str](
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
