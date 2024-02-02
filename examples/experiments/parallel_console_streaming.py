import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from uuid import uuid4

from funcchain import achain, settings
from funcchain.backend.streaming import astream_to
from funcchain.utils.token_counter import count_tokens
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel


class RenderChain:
    def __init__(self, renderer: "Renderer", name: str) -> None:
        self.id = uuid4().hex
        self.name = name
        self.renderer = renderer
        self.renderer.add_chain(self)

    def render_stream(self, token: str) -> None:
        self.renderer.render_stream(token, self)

    def close(self) -> None:
        self.renderer.remove(self)


class Renderer:
    def __init__(self, column_height: int = 3) -> None:
        self.column_height = column_height
        self.console = Console(height=3)
        self.layout = Layout()
        self.live = Live(console=self.console, auto_refresh=True, refresh_per_second=30)
        self.chains: list[RenderChain] = []

    def add_chain(self, chain: RenderChain) -> None:
        if not self.live.is_started:
            self.live.start()
        self.console.height = (len(self.layout.children) + 1) * self.column_height
        self.layout.split_column(*self.layout.children, Layout(name=chain.id, size=self.column_height))
        self.chains.append(chain)

    def render_stream(self, token: str, chain: RenderChain) -> None:
        prev = ""
        tokens: int = 0
        max_width: int = self.console.width
        content_width: int = 0
        if isinstance(panel := self.layout[chain.id]._renderable, Panel) and isinstance(panel.renderable, str):
            content_width = self.console.measure(panel.renderable).maximum
            if isinstance(panel.title, str) and " " in panel.title:
                tokens = int(panel.title.split(" ")[1])
            tokens += count_tokens(token)
            prev = panel.renderable.replace("\n", " ")
            if (max_width - content_width - 5) < 1:
                prev = prev[len(token) :] + token
            else:
                prev += token
        else:
            prev += token
        self.layout[chain.id].update(Panel(prev, title=f"({chain.name}) {tokens} tokens"))
        self.live.update(self.layout)

    def remove(self, chain: RenderChain) -> None:
        self.chains.remove(chain)
        self.layout.split_column(*(child for child in self.layout.children if child.name != chain.id))
        self.console.height = (len(self.layout.children)) * self.column_height
        self.live.update(self.layout)
        if not self.chains:
            self.live.update(self.layout)
            self.live.stop()

    def __del__(self) -> None:
        self.live.stop()


async def generate_poem_async(topic: str) -> str:
    """
    Write a short story based on the topic.
    """
    return await achain()


@asynccontextmanager
async def log_stream(renderer: Renderer, name: str) -> AsyncGenerator:
    render_chain = RenderChain(renderer, name)
    async with astream_to(render_chain.render_stream):
        yield render_chain

    render_chain.close()


async def stream_poem_async(renderer: Renderer, topic: str) -> None:
    async with log_stream(renderer, topic):
        await generate_poem_async(topic)


async def main() -> None:
    settings.llm = "openai/gpt-3.5-turbo-1106"

    topics = ["goldfish", "spacex", "samurai", "python", "javascript", "ai"]
    renderer = Renderer()

    for topic in topics:
        task = asyncio.create_task(stream_poem_async(renderer, topic))
        await asyncio.sleep(1)

    while not task.done():
        await asyncio.sleep(1)


asyncio.run(main())
print("done")
