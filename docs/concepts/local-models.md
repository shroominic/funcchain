# Local Models

Funcchain supports local models through the [llama.cpp](https://github.com/ggerganov/llama.cpp) project using the [llama_cpp_python](https://llama-cpp-python.readthedocs.io/en/latest/) bindings.

## LlamaCPP

Written in highly optimized C++ code, LlamaCPP is a library for running large language models locally.
It uses GGUF files which are a binary format for storing quantized versions of large language models.
You can download alot of GGUF models from TheBloke on huggingface.

## Grammars

Context Free Grammars are a powerful abstraction for a deterministic shape of a string.
Funcchain utilizes this by forcing local models to respond in a structured way.

For example you can create a grammar that forces the model to always respond with a json object.
This is useful if you want to use the output of the model in your code.

Going one step further you can also create a grammar that forces the model to respond with a specific pydantic model.

This is how funcchain is able to use local models in a structured way.
