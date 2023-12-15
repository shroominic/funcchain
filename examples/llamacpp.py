from pydantic import BaseModel, Field

from funcchain import chain, settings
from funcchain.streaming import stream_to


# define your model
class SentimentAnalysis(BaseModel):
    analysis: str = Field(description="A description of the analysis")
    sentiment: bool = Field(description="True for Happy, False for Sad")


# define your prompt
def analyze(text: str) -> SentimentAnalysis:
    """
    Determines the sentiment of the text.
    """
    return chain()


if __name__ == "__main__":
    # set global llm
    settings.llm = "gguf/openhermes-2.5-mistral-7b"

    # log tokens as stream to console
    with stream_to(print):
        # run prompt
        poem = analyze("I really like when my dog does a trick!")

    # print final parsed output
    from rich import print

    print(poem)
