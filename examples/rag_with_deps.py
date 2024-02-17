from operator import itemgetter
from typing import Annotated

from funcchain.syntax import chain, runnable
from funcchain.syntax.params import Depends
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS

retriever = FAISS.from_texts(
    [
        "cold showers are good for your immune system",
        "i dont like when people are mean to me",
        "japanese tea is full of heart warming flavors",
    ],
    embedding=OpenAIEmbeddings(),
).as_retriever(
    search_kwargs={"k": 1},
)


@runnable
def poem_with_retrieval(
    topic: str,
    context: Annotated[str, Depends(itemgetter("topic") | retriever)],
) -> str:
    """
    Generate a poem about the topic with the given context.
    """
    return chain()


print(
    poem_with_retrieval.invoke({"topic": "love"}),
)
