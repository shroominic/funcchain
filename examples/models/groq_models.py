from funcchain import chain, settings
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from rich import print


class SentimentAnalysis(BaseModel):
    analysis: str = Field(description="A description of the analysis")
    sentiment: bool = Field(description="True for Happy, False for Sad")


def analyze(text: str) -> SentimentAnalysis:
    """
    Determines the sentiment of the text.
    """
    return chain()


if __name__ == "__main__":
    # set global llm
    settings.llm = ChatGroq(model="llama3-70b-8192")

    # run prompt
    result = analyze("I really like when my dog does a trick!")

    # show final parsed output
    print(result)
