from funcchain.syntax import chain, runnable
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_openai.embeddings import OpenAIEmbeddings


@runnable
def generate_poem(topic: str, context: str) -> str:
    """
    Generate a poem about the topic with the given context.
    """
    return chain()


vectorstore = FAISS.from_texts(
    [
        "japanese tea is full of heart warming flavors",
        "in the morning you should take a walk",
        "cold showers are good for your health",
    ],
    embedding=OpenAIEmbeddings(),
)
retriever = vectorstore.as_retriever()

retrieval_chain: Runnable = {
    "context": retriever,
    "topic": RunnablePassthrough(),
} | generate_poem


print(retrieval_chain.invoke("love"))
