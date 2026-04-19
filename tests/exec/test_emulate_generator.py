import pytest
import asyncio
from typing import Iterator, AsyncIterator, List
from OpenHosta import emulate, emulate_async
from OpenHosta.core.base_model import ModelCapabilities
from OpenHosta.models.OpenAICompatible import OpenAICompatibleModel

class MockCodeBlockModel(OpenAICompatibleModel):
    def __init__(self, blocks: List[str]):
        super().__init__(model_name="mock-code-block")
        self.model_name = "mock-code-block"
        self.capabilities = {ModelCapabilities.STREAMING, ModelCapabilities.TEXT2TEXT}
        self.blocks = blocks

    def _generate_stream_without_retry(self, messages, **kwargs):
        for block in self.blocks:
            yield "```python\n"
            yield block + "\n"
            yield "```\n"

    async def generate_stream_async(self, messages, **kwargs):
        for block in self.blocks:
            await asyncio.sleep(0.01)
            yield "```python\n"
            yield block + "\n"
            yield "```\n"

    def generate(self, messages, **kwargs):
        content = ""
        for block in self.blocks:
            content += f"```python\n{block}\n```\n"
        return {"choices": [{"message": {"content": content}}]}

# Create a custom pipeline to avoid actual API calls during tests
from OpenHosta.pipelines import OneTurnConversationPipeline
import copy

def get_mock_pipeline(blocks: List[str]):
    pipeline = OneTurnConversationPipeline(model_list=[MockCodeBlockModel(blocks)])
    return pipeline

def test_emulate_sync_generator():
    pipeline = get_mock_pipeline(["1", "2", "3"])
    
    def my_gen() -> Iterator[int]:
        """A test docstring."""
        yield from emulate(pipeline=pipeline)
        
    results = list(my_gen())
    assert results == [1, 2, 3]

def test_emulate_sync_value():
    # When not a generator, emulate returns a single value 
    # (the first block pulled by pull_extract_data_section)
    pipeline = get_mock_pipeline(["42"])
    
    def my_val() -> int:
        """A test docstring."""
        return emulate(pipeline=pipeline)
        
    result = my_val()
    assert result == 42

@pytest.mark.asyncio
async def test_emulate_async_generator():
    pipeline = get_mock_pipeline(["10", "20"])
    
    async def my_async_gen() -> AsyncIterator[int]:
        """A test docstring."""
        async for x in await emulate_async(pipeline=pipeline):
            yield x
            
    results = []
    async for item in my_async_gen():
        results.append(item)
    assert results == [10, 20]

@pytest.mark.asyncio
async def test_emulate_async_value():
    pipeline = get_mock_pipeline(["100"])
    
    async def my_async_val() -> int:
        """A test docstring."""
        return await emulate_async(pipeline=pipeline)
        
    result = await my_async_val()
    assert result == 100
