from langchain.chat_models.llamacpp import ChatLlamaCpp
from pydantic import BaseModel

from funcchain import chain, settings
from funcchain.streaming import stream_to
from funcchain.utils.grammar import grammar_from_


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
    grammar = grammar_from_(Poem)

    settings.LLM = ChatLlamaCpp(
        verbose=False,
        model_path=".models/openhermes-2.5-mistral-7b.Q4_K_M.gguf",
        streaming=True,
        n_ctx=2048,
        max_tokens=512,
        grammar=grammar,
        stop=["</s>"],
    )

    with stream_to(print):
        poem = generate_poem("llama")

    from rich import print

    print(poem)
