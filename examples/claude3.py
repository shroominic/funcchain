from typing import Annotated

from funcchain import Depends, chain, settings
from langchain.document_loaders.pdf import PyPDFLoader

settings.llm = "anthropic/claude-3-opus-20240229"


def load_pdf(input: dict) -> str:
    if path := input.get("path"):
        return " ".join([d.page_content for d in PyPDFLoader(path).load()])
    return "No URL given"


def summarize_pdf(path: str, pdf: Annotated[str, Depends(load_pdf)] = "") -> str:
    """
    Given the full pdf summarize the entire document and focus on the most important parts.
    """
    return chain()


path = "~/Downloads/muzio1966.pdf"

summary = summarize_pdf(path)

print(summary)
