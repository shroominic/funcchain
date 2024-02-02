# Streaming

Streaming is important if you want to do things with your LLM generation while the LLM is still generating.
This can enhance the user experience by already showing part of the response but you could also stop a generation early if it does not match certain requirements.

## Console Log Streaming

If you want to stream all the tokens generated quickly to your console output,
you can use the `settings.console_stream = True` setting.

## `stream_to()` wrapper

For streaming with non runnable funcchains you can wrap the LLM generation call into the `stream_to()` context manager. This would look like this:

```python
def summarize(text: str) -> str:
    """Summarize the text."""
    return chain()

text = "... a large text"

with stream_to(print):
    summarize(text)
```

This will call token by token the print function so it will show up in your console.
But you can also insert any function that accepts a string to create your custom stream handlers.

You can also use `async with stream_to(your_async_handler):` for async streaming.
Make sure summarize is then created using `await achain()`.

## LangChain runnable streaming

If you can compile every funcchain into a langchain runnable and then use the native langchain syntax for streaming:

```python
@runnable
def summarize(text: str) -> str:
    """Summarize the text."""
    return chain()

text = "... a large text"

for chunk in summarize.stream(input={"text": text}):
    print(chunk, end="", flush=True)
```
