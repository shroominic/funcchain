from funcchain import chain, settings
from funcchain.syntax.output_types import CodeBlock


def generate_code(instruction: str) -> CodeBlock:
    return chain(instruction=instruction)


if __name__ == "__main__":
    settings.llm = "ollama/openhermes-2.5-mistral-7b"
    settings.console_stream = True

    block = generate_code("Write a script that generates a sin wave.")

    print("\033c")
    print(block.code)
