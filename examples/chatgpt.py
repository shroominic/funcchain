"""
Simple chatgpt rebuild with memory/history.
"""
from funcchain import chain
from langchain.memory import ChatMessageHistory


history = ChatMessageHistory()


def ask(question: str) -> str:
    return chain(
        instruction=question,
        system="You are an advanced AI Assistant.",
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

        print("AI:", ask(query))


if __name__ == "__main__":
    print("Hey! How can I help you?")
    chat_loop()
