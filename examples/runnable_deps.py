from typing import Annotated

from funcchain import chain, runnable
from funcchain.syntax.params import Depends


def get_relevant_files() -> str:
    """
    Get the relevant files from the codebase tree.
    """
    return "relevant_files"


@runnable
def codebase_answer(
    user_question: str,
    relevant_files: Annotated[str, Depends(get_relevant_files)],
) -> str:
    """
    Answer the question based on the codebase tree and relevant files.
    """
    return chain()
