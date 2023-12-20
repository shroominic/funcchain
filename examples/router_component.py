from funcchain.components import ChatRouter


def handle_pdf_requests(user_query: str) -> None:
    print("Handling PDF requests with user query: ", user_query)


def handle_csv_requests(user_query: str) -> None:
    print("Handling CSV requests with user query: ", user_query)


def handle_default_requests(user_query: str) -> None:
    print("Handling DEFAULT requests with user query: ", user_query)


router = ChatRouter(
    routes={
        "pdf": {
            "handler": handle_pdf_requests,
            "description": "Call this for requests including PDF Files.",
        },
        "csv": {
            "handler": handle_csv_requests,
            "description": "Call this for requests including CSV Files.",
        },
        "default": handle_default_requests,
    },
)


router.invoke_route("Can you summarize this csv?")
