import base64
from typing import Any, Dict, Optional, Union

import requests  # type: ignore
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.pydantic_v1 import validator

try:
    from langchain_community.chat_models import ChatOllama as _ChatOllama

    class ChatOllama(_ChatOllama):
        grammar: Optional[str] = None
        """
        The [GBNF](https://github.com/ggerganov/llama.cpp/tree/master/grammars) grammar used to constrain the output.
        """

        @validator("grammar")
        def _validate_grammar(cls, v: Optional[str]) -> Optional[str]:
            if v is not None and "root ::=" not in v:
                raise ValueError("Grammar must contain a root rule.")
            return v

        @property
        def _default_params(self) -> Dict[str, Any]:
            """Get the default parameters for calling Ollama."""
            return {
                "model": self.model,
                "format": self.format,
                "options": {
                    "mirostat": self.mirostat,
                    "mirostat_eta": self.mirostat_eta,
                    "mirostat_tau": self.mirostat_tau,
                    "num_ctx": self.num_ctx,
                    "num_gpu": self.num_gpu,
                    "num_thread": self.num_thread,
                    "repeat_last_n": self.repeat_last_n,
                    "repeat_penalty": self.repeat_penalty,
                    "temperature": self.temperature,
                    "stop": self.stop,
                    "tfs_z": self.tfs_z,
                    "top_k": self.top_k,
                    "top_p": self.top_p,
                    "grammar": self.grammar,  # added
                },
                "system": self.system,
                "template": self.template,
            }

        def _convert_messages_to_ollama_messages(
            self, messages: list[BaseMessage]
        ) -> list[dict[str, Union[str, list[str]]]]:
            ollama_messages = []
            for message in messages:
                role = ""
                if isinstance(message, HumanMessage):
                    role = "user"
                elif isinstance(message, AIMessage):
                    role = "assistant"
                elif isinstance(message, SystemMessage):
                    role = "system"
                else:
                    raise ValueError("Received unsupported message type for Ollama.")

                content = ""
                images = []
                if isinstance(message.content, str):
                    content = message.content
                else:
                    image_urls = []
                    for content_part in message.content:
                        if isinstance(content_part, str):
                            content += f"\n{content_part}"
                        elif content_part.get("type") == "text":
                            content += f"\n{content_part['text']}"
                        elif content_part.get("type") == "image_url":
                            if isinstance(content_part.get("image_url"), str):
                                if content_part["image_url"].startswith("data:"):
                                    image_url_components = content_part["image_url"].split(",")
                                    # Support data:image/jpeg;base64,<image> format
                                    # and base64 strings
                                    if len(image_url_components) > 1:
                                        images.append(image_url_components[1])
                                    else:
                                        images.append(image_url_components[0])
                                else:
                                    image_urls.append(content_part["image_url"])
                            else:
                                if isinstance(content_part.get("image_url"), dict):
                                    if content_part["image_url"]["url"].startswith("data:"):
                                        image_url_components = content_part["image_url"]["url"].split(",")
                                        # Support data:image/jpeg;base64,<image> format
                                        # and base64 strings
                                        if len(image_url_components) > 1:
                                            images.append(image_url_components[1])
                                        else:
                                            images.append(image_url_components[0])
                                    else:
                                        image_urls.append(content_part["image_url"]["url"])
                                else:
                                    raise ValueError("Unsupported message content type.")
                        else:
                            raise ValueError(
                                "Unsupported message content type. "
                                "Must either have type 'text' or type 'image_url' "
                                "with a string 'image_url' field."
                            )
                    # download images and append base64 strings
                    if image_urls:
                        for image_url in image_urls:
                            response = requests.get(image_url)
                            if response.status_code == 200:
                                image = response.content
                                images.append(base64.b64encode(image).decode("utf-8"))
                            else:
                                raise ValueError(f"Failed to download image from {image_url}.")

                ollama_messages.append(
                    {
                        "role": role,
                        "content": content,
                        "images": images,
                    }
                )

            return ollama_messages  # type: ignore


except ImportError:

    class ChatOllama:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ImportError("Please install langchain_community to use ChatOllama.")
