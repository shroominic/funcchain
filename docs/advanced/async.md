# Async

## Why and how to use using async?

Asyncronous promgramming is a way to easily parallelize processes in python.
This is very useful when dealing with LLMs because every request takes a long time and the python interpreter should do alot of other things in the meantime instead of waiting for the request.

Checkout [this brillian async tutorial](https://fastapi.tiangolo.com/async/) if you never coded in an asyncronous way.

## Async in FuncChain

You can use async in funcchain by creating your functions using `achain()` instead of the normal `chain()`.
It would then look like this:

```python
from funcchain import achain

async def generate_poem(topic: str) -> str:
    """
    Generate a poem inspired by the given topic.
    """
    return await achain()
```

You can then `await` the async `generate_poem` function inside another async funtion or directly call it using `asyncio.run(generate_poem("birds"))`.

## Async in LangChain

When converting your funcchains into a langchain runnable you can use the native langchain way of async.
This would be `.ainvoke(...)`, `.astream(...)` or `.abatch(...)` .

## Async Streaming

You can use langchains async streaming interface but also use the `stream_to(...)` wrapper (explained [here](../concepts/streaming.md#strem_to-wrapper)) as an async context manager.

```python
async with stream_to(...):
    await ...
```
