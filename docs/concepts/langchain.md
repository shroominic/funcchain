# LangChain

## What is LangChain?

[LangChain](https://python.langchain.com/docs/get_started/introduction) is the most advanced library for building applications using large language models.
Funcchain is built on top of `langchain_core` which inculdes [LangChain Expression Language (LCEL)](https://python.langchain.com/docs/expression_language/get_started) and alot more powerful core abstractions for building cognitive architectures.

## Why building on top of it?

We have been looking into alot of different libraries and wanted to start a llm framework from scratch.
But langchain already provides alot of the core abstractions we need to use and it is the most advanced library we have found so far.

## Compatibility

Funcchain is compatible with all langchain chat models, memory stores and runnables.
It's using langchain output parsers and the templating system.
On the other hand langchain is compatible with funcchain by using the `@runnable` decorator.
This will convert your function into a runnable that can be used in LCEL so you can build your own complex cognitive architectures.

## TODO: add runnable example
