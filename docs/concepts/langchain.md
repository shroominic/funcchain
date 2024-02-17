# LangChain

## What is LangChain?

[LangChain](https://python.langchain.com/docs/get_started/introduction) is the most advanced library for building applications using large language models.
Funcchain is built on top of `langchain_core` which inculdes [LangChain Expression Language (LCEL)](https://python.langchain.com/docs/expression_language/get_started) and alot more powerful core abstractions for building cognitive architectures.

## Why building on top of it?

We have been looking into alot of different libraries and wanted to start a llm framework from scratch.
But langchain already provides all of the fundamental abstractions we need to use and it is the most advanced library we have found so far.

## Compatibility

Funcchain is compatible with all langchain chat models, memory stores and runnables.
It's using langchain output parsers and the templating system.
On the other hand langchain is compatible with funcchain by using the `@runnable` decorator.
This will convert your function into a runnable that can be used in LCEL so you can build your own complex cognitive architectures.

## LCEL Example (RAG)

```python
from funcchain import chain, runnable
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_community.embeddings import OpenAIEmbeddings

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
    "context": retriever,
    "topic": RunnablePassthrough(),
} | generate_poem

print(retrieval_chain.invoke("love"))
```

The chain will then retrieve ´japanese tea is full of heart warming flavors` as context since it's the most similar to the topic "love".

```bash
# => In a cup of tea, love's warmth unfurls
#    Japanese flavors, heartwarming pearls
#    A sip of love, in every swirl
#    In Japanese tea, love's essence twirls
```

<!-- markdownlint-disable MD033 MD046 -->

!!! Useful
    For seeing whats going on inside the LLM you should try the Langsmith integration:
    Add those lines to .env and funcchain will use langsmith tracing.

    ```bash
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_API_KEY="ls__api_key"
    LANGCHAIN_PROJECT="PROJECT_NAME"
    ```

    Langsmith is used to understand what happens under the hood of your LLM generations.
    When multiple LLM calls are used for an output they can be logged for debugging.
