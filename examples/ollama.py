from langchain.chat_models import ChatOllama
from funcchain import chain, settings
from funcchain.streaming import stream_to
from pydantic import BaseModel


settings.LLM = ChatOllama(model="openhermes2.5-mistral", format="json")
settings.STREAMING = True


class Startup(BaseModel):
    name: str
    description: str
    keywords: list[str]


def generate_startup_name(idea: str) -> Startup:
    """
    Generate a startup concept based on the idea.
    """
    return chain()


with stream_to(print):
    idea = "AI coding assistant as cli tool"
    startup = generate_startup_name(idea)

    print(f"{startup.name=}")
    print(f"{startup.description=}")

    for keyword in startup.keywords:
        print(f"{keyword=}")
