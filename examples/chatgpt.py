"""
Simple chatgpt rebuild with memory/history.
"""

from funcchain import chain, settings
from funcchain.utils.memory import ChatMessageHistory

settings.llm = "openai/gpt-4"
settings.console_stream = True

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

        ask(query)


if __name__ == "__main__":
    print("Hey! How can I help you?\n")
    chat_loop()
