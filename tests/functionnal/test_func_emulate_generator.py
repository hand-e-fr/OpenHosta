import pytest
import os
from typing import Iterator, AsyncIterator
from dotenv import load_dotenv
from asyncio import run

load_dotenv()

from OpenHosta import emulate, emulate_async

def test_emulate_sync_generator_basic():
    """Test emulate() inside a synchronous generator returns typed items."""
    
    def generate_even_numbers() -> Iterator[int]:
        """
        Generate exactly 3 even numbers sequentially, starting from 2.
        For example: 2, 4, 6.
        """
        yield from emulate()
        
    items = list(generate_even_numbers())
    
    # We requested 3 numbers, the LLM should give us roughly that.
    # At a minimum it should be an iterable of ints.
    assert len(items) >= 1, "Expected at least 1 item"
    for item in items:
        assert isinstance(item, int), f"Expected int, got {type(item)}"
        assert item % 2 == 0, f"Expected even number, got {item}"

def test_emulate_async_generator_basic():
    """Test emulate_async() inside an asynchronous generator returns typed items."""
    
    async def app():
        async def generate_vowels() -> AsyncIterator[str]:
            """
            Generate the 5 basic vowels (a, e, i, o, u) one by one.
            """
            async for vowel in emulate_async():
                yield vowel
                
        results = []
        async for v in generate_vowels():
            results.append(v.lower())
        return results

    vowels = run(app())
    assert len(vowels) >= 3, "Expected at least 3 vowels generated"
    assert "a" in vowels, "Missing 'a'"

def test_emulate_generator_dataclass():
    from dataclasses import dataclass

    @dataclass
    class President:
        name: str
        start_date: str
        end_date: str

    def list_presidents() -> Iterator[President]:
        """
        List 2 presidents of France.
        """
        yield from emulate()

    items = list(list_presidents())
    assert len(items) >= 1
    for item in items:
        assert isinstance(item, President)
        assert hasattr(item, "name")
        assert hasattr(item, "start_date")
        assert hasattr(item, "end_date")
