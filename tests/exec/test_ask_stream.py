import pytest
import asyncio
from typing import Iterator, AsyncIterator
import OpenHosta
from OpenHosta.core.base_model import ModelCapabilities
from OpenHosta.models.OpenAICompatible import OpenAICompatibleModel

class MockStreamingModel(OpenAICompatibleModel):
    def __init__(self, chunks, **kwargs):
        super().__init__(model_name="mock-streamer")
        self.model_name = "mock-streamer"
        self.capabilities = {ModelCapabilities.STREAMING, ModelCapabilities.TEXT2TEXT}
        self.chunks = chunks

    def _generate_stream_without_retry(self, messages, **kwargs):
        for chunk in self.chunks:
            yield chunk

    async def generate_stream_async(self, messages, **kwargs):
        for chunk in self.chunks:
            await asyncio.sleep(0.01)
            yield chunk

    def generate(self, messages, **kwargs):
        return {"choices": [{"message": {"content": "".join(self.chunks)}}]}


def test_ask_stream_sync():
    model = MockStreamingModel(["Hello", " ", "World", "!"])
    # interval_ms=0 means yield every chunk as it arrives
    chunks = list(OpenHosta.ask_stream("Say hello", model=model, interval_ms=0))
    assert chunks == ["Hello", " ", "World", "!"]


@pytest.mark.asyncio
async def test_ask_stream_async():
    model = MockStreamingModel(["Hello", " ", "Async", "!"])
    chunks = []
    async for chunk in OpenHosta.ask_stream_async("Say hello", model=model, interval_ms=0):
        chunks.append(chunk)
    assert chunks == ["Hello", " ", "Async", "!"]

def test_ask_stream_interval():
    import time
    
    class SlowModel(OpenAICompatibleModel):
        def __init__(self):
            super().__init__(model_name="slow")
            self.model_name = "slow"
            self.capabilities = {ModelCapabilities.STREAMING, ModelCapabilities.TEXT2TEXT}
        def _generate_stream_without_retry(self, messages, **kwargs):
            # yield quickly
            yield "A"
            yield "B"
            # wait a bit to trigger interval
            time.sleep(0.06)
            yield "C"
            
    # With interval=50ms, 'A' and 'B' should be grouped, then 'C' flushed at the end
    model = SlowModel()
    chunks = list(OpenHosta.ask_stream("Slow", model=model, interval_ms=50))
    assert chunks == ["AB", "C"]
