import pytest
import os
from dotenv import load_dotenv

load_dotenv()

from OpenHosta import ask_stream, ask_stream_async
from asyncio import run

def test_ask_stream_basic():
    """Test that ask_stream yields chunks that form a complete answer."""
    prompt = "Spell the word 'hello' letter by letter. Do not add any punctuation or extra text."
    chunks = list(ask_stream(prompt, interval_ms=10))
    
    full_response = "".join(chunks).lower()
    
    assert len(chunks) >= 1, "Expected at least one chunk to be returned"
    assert "h" in full_response and "e" in full_response and "l" in full_response and "o" in full_response, f"Expected letters of 'hello' in response, got: {full_response}"

def test_ask_stream_async_basic():
    """Test that ask_stream_async yields chunks that form a complete answer."""
    async def app():
        prompt = "Count to 3: 1, 2, 3"
        chunks = []
        async for chunk in ask_stream_async(prompt, interval_ms=10):
            chunks.append(chunk)
        return chunks

    chunks = run(app())
    full_response = "".join(chunks)
    
    assert len(chunks) >= 1, "Expected at least one chunk"
    assert "1" in full_response and "3" in full_response, f"Expected numbers in response, got: {full_response}"
