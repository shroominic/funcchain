from pydantic import BaseModel, Field, field_validator

from funcchain import chain, settings
from funcchain._llms import ChatLlamaCpp
from funcchain.streaming import stream_to


# define your model
class SentimentAnalysis(BaseModel):
    sentiment: bool = Field(description="True for Happy, False for Sad")
    score: int = Field(description="The confidence score of the analysis")

    # example how a retry validator would look like:
    @field_validator("score")
    def check_score(cls, v: int) -> int:
        if v < 10 or v > 100:
            raise ValueError("Score must be between 10 and 100")
        return v


# define your prompt
def analyze(topic: str) -> SentimentAnalysis:
    """
    Determines the sentiment of the topic
    """
    return chain()


if __name__ == "__main__":
    # set global LLM
    settings.LLM = ChatLlamaCpp(
        model_path=".models/openhermes-2.5-neural-chat-7b-v3-1-7b.Q5_K_M.gguf"
    )

    # log tokens as stream to console
    with stream_to(print):
        # run prompt
        poem = analyze("I really like when my dog does a trick")

    # print final parsed output
    from rich import print

    print(poem)
