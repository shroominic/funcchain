from operator import itemgetter

from funcchain.syntax import chain, runnable
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.runnables import Runnable, RunnablePassthrough


@runnable
def generate_poem(topic: str, context: str) -> str:
    """
    Generate a poem about the topic with the given context.
    """
    return chain()


vectorstore = FAISS.from_texts(
    [
        "cold showers are good for your immune system",
        "i dont like when people are mean to me",
        "japanese tea is full of heart warming flavors",
    ],
    embedding=OpenAIEmbeddings(),
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 1})

retrieval_chain: Runnable = {
    "context": itemgetter("topic") | retriever,
    "topic": RunnablePassthrough(),
} | generate_poem

print(retrieval_chain.invoke({"topic": "love"}))
