from pydantic import BaseModel

from funcchain import chain, settings
from funcchain._llms import ChatLlamaCpp
from funcchain.streaming import stream_to


class Keyword(BaseModel):
    word: str
    rating: int


class Poem(BaseModel):
    topic: str
    content: str
    keywords: list[Keyword]


def generate_poem(topic: str) -> Poem:
    """
    Generate a poem about the topic.
    """
    return chain()


if __name__ == "__main__":
    settings.LLM = ChatLlamaCpp(
        verbose=False,
        model_path=".models/openhermes-2.5-mistral-7b.Q4_K_M.gguf",
        streaming=True,
        n_ctx=2048,
        max_tokens=512,
    )

    with stream_to(print):
        poem = generate_poem("llama")

    from rich import print

    print(poem)
