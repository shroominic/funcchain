"""
Simple chatgpt rebuild with memory/history.
"""
from funcchain import chain, settings
from funcchain.streaming import stream_to
from langchain.memory import ChatMessageHistory

settings.STREAMING = True

history = ChatMessageHistory()


def ask(question: str) -> str:
    return chain(
        system="You are an advanced AI Assistant.",
        instruction=question,
        memory=history,
    )


def chat_loop() -> None:
    while True:
        query = input("> ")

        if query == "exit":
            break

        if query == "clear":
            global history
            history.clear()
            print("\033c")
            continue

        with stream_to(print):
            ask(query)


if __name__ == "__main__":
    print("Hey! How can I help you?\n")
    chat_loop()
