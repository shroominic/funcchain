def count_tokens(text: str, model: str = "gpt-4") -> int:
    if "gpt-4" in model:
        from tiktoken import encoding_for_model

        return len(encoding_for_model(model).encode(text))
    else:
        raise NotImplementedError("Please sumbmit a PR or write an issue with your desired model.")
