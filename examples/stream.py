from funcchain import chain, settings
from funcchain.backend.streaming import stream_to

settings.temperature = 1


def generate_story_of(topic: str) -> str:
    """
    Write a short story based on the topic.
    """
    return chain()


with stream_to(print):
    generate_story_of("a space cat")
