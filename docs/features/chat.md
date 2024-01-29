# ChatGPT rebuild with memory/history

!!! Example
    chatgpt.py [Example](https://github.com/shroominic/funcchain/blob/main/examples/chatgpt.py)

!!! Important
    Ensure you have set up your API key for the LLM of your choice, or Funcchain will look for a `.env` file. So in `.env` set up your key.

    ```bash
    OPENAI_API_KEY="sk-rnUBxirFQ4bmz2Ae4qyaiLShdCJcsOsTg"
    ```

## Code Example

<pre><code id="codeblock">
```python
from funcchain import chain, settings
from funcchain.utils.memory import ChatMessageHistory

settings.llm = "openai/gpt-4"
settings.console_stream = True

history = ChatMessageHistory()

def ask(question: str) -> str:
    return chain(
        system="You are an advanced AI Assistant.",
        instruction=question,
        memory=history,
    )

def chat_loop() -> None:
    while True:
        query = input("> ")

        if query == "exit":
            break

        if query == "clear":
            global history
            history.clear()
            print("\033c")
            continue

        ask(query)

if __name__ == "__main__":
    print("Hey! How can I help you?\n")
    chat_loop()
```
</code></pre>

<div class="termy">
    ```terminal
    initial print function:
    $ Hey! How can I help you?
    $ >

    userprompt:
    $ > Say that Funcchain is cool

    assistant terminal asnwer:
    $ Funcchain is cool.
    ```

</div>

## Instructions

!!! Step-by-Step
    **Import nececary funcchain components**

    ```python
    from funcchain import chain, settings
    from funcchain.utils.memory import ChatMessageHistory
    ```

    **Settings**

    ```python
    settings.llm = "openai/gpt-4"
    settings.console_stream = True
    ```


    Funcchain supports multiple LLMs and has the ability to stream received LLM text instead of waiting for the complete answer. For configuration options, see below:

    ```markdown
    - `settings.llm`: Specify the language model to use. See MODELS.md for available options.
    - Streaming: Set `settings.console_stream` to `True` to enable streaming,
        or `False` to disable it.
    ```

    [MODELS.md](https://github.com/shroominic/funcchain/blob/main/MODELS.md)


    **Establish a chat history**

    ```python
    history = ChatMessageHistory()
    ```
    Stores messages in an in memory list. This will crate a thread of messages.

    See [memory.py] //Todo: Insert Link


    **Define ask function**
    See how funcchain uses `chain()` with an input `str` to return an output of type  `str`

    ```python
    def ask(question: str) -> str:
    return chain(
    system="You are an advanced AI Assistant.",
    instruction=question,
    memory=history,
    )
    ```

    This function sends a question to the Funcchain `chain()` function.

    It sets the system context as an advanced AI Assistant and passes the question as an instruction.

    The history object is used to maintain a thread of messages for context.

    The function returns the response from the chain function.
