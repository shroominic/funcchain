# Union Types

You can use union types in funcchain to make the model select one of multiple PydanticModels for the response.
You may have seen this in the [Complex Example](../index.md#complex-example).

## Errors

One good usecase for this is to always give the LLM the chance to raise an Error if the input is strange or not suited. You can check this in more detail [here](errors.md).

## Agents

Another usecase is to create an Agent like chain that selects one of multiple tools.
Every PydanticModel then represents the input schema of your function and you can even override the `__call__` method of your models to directly execute the tool if you need so.

## Function Calling

Under the hood the union type featur uses openai tool_calling, especially the functionallity to give the LLM multiple tools to choose from.
All pydantic models then get injected as available tools and the LLM is forced to call one of them.
