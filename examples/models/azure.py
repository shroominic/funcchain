from funcchain import chain, settings
from pydantic import BaseModel, Field


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
    settings.llm = "azure/gpt-4o"
    # log tokens as stream to console
    settings.console_stream = True

    # run prompt
    poem = analyze("I really like when my dog does a trick!")

    # show final parsed output
    print(poem)
