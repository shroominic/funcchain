from funcchain import chain, settings
from funcchain.streaming import stream_to

settings.MODEL_TEMPERATURE = 1
settings.MODEL_NAME = "gpt-3.5-turbo-1106"
settings.STREAMING = True


def generate_story_of(topic: str) -> str:
    """
    Write a short story based on the topic.
    """
    return chain()


with stream_to(print):
    generate_story_of("a space cat")
