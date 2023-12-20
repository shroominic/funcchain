from funcchain.components import ChatRouter


def handle_pdf_requests(user_query: str) -> str:
    return f"Handling PDF requests with user query: {user_query}"


def handle_csv_requests(user_query: str) -> str:
    return f"Handling CSV requests with user query: {user_query}"


def handle_default_requests(user_query: str) -> str:
    return f"Handling DEFAULT requests with user query: {user_query}"


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


def test_router() -> None:
    assert "Handling CSV" in router.invoke_route("Can you summarize this csv?")

    assert "Handling PDF" in router.invoke_route("Can you summarize this pdf?")

    assert "Handling DEFAULT" in router.invoke_route("Hey, whatsup?")


if __name__ == "__main__":
    test_router()
