from funcchain import settings
from funcchain.model.patches.llamacpp import ChatLlamaCpp

settings.llm = ChatLlamaCpp(  # type: ignore
    model_path="./.models/your-model.gguf",
    n_gpu_layers=50,
    repeat_penalty=1.0,
)
