from funcchain import chain, settings
from pydantic import BaseModel

settings.console_stream = True
settings.llm = "llamacpp/openchat-3.5-0106:Q3_K_M"


class Output(BaseModel):
    plot: str
    kwargs: dict


def get_kwargs(user_query: str) -> Output:
    """
    Translate the user query to a dictionary of kwargs
    """
    return chain()


print(get_kwargs("scatter(color='red')"))
