from funcchain.components import ChatRouter


def handle_pdf_requests(user_query: str) -> str:
    return f"Handling PDF requests with user query: {user_query}"


def handle_csv_requests(user_query: str) -> str:
    return f"Handling CSV requests with user query: {user_query}"


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
            "handler": lambda x: f"Handling DEFAULT with user query: {x}",
            "description": "Call this for all other requests.",
        },
    },
)


def test_router() -> None:
    assert "Handling CSV" in router.invoke_route("Can you summarize this csv?")

    assert "Handling PDF" in router.invoke_route("Can you summarize this pdf?")

    assert "Handling DEFAULT" in router.invoke_route("whatsup")

    assert "Handling DEFAULT" in router.invoke_route(
        "I want to book a flight how to do this?"
    )


if __name__ == "__main__":
    test_router()
