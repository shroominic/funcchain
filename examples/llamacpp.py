from pydantic import BaseModel, Field, field_validator

from funcchain import chain, settings
from funcchain._llms import ChatLlamaCpp
from funcchain.streaming import stream_to


class SentimentAnalysis(BaseModel):
    sentiment: bool = Field(description="True for Happy, False for Sad")
    score: int = Field(description="The score of the sentiment")

    @field_validator("score")
    def check_score(cls, v: int) -> int:
        if v < 10 or v > 100:
            raise ValueError("Score must be between 10 and 100")
        return v


def analyze(topic: str) -> SentimentAnalysis:
    """
    Determines the sentiment of the topic
    """
    return chain()


if __name__ == "__main__":
    settings.LLM = ChatLlamaCpp(
        verbose=False,
        model_path=".models/openhermes-2.5-neural-chat-7b-v3-1-7b.Q5_K_M.gguf",
        # streaming=True,
        n_ctx=4096,
        # n_gpu_layers=0,
        max_tokens=512,
    )

    with stream_to(print):
        poem = analyze("I really like when my dog does a trick")

    from rich import print

    print(poem)
