import pytest
from dotenv import load_dotenv
load_dotenv()

from OpenHosta import ask, emulate

def test_smoke_ask():
    """Verify that ask works for a simple query."""
    response = ask("Say 'Hello, World!'")
    assert "Hello" in response or "world" in response.lower()

def test_smoke_emulate():
    """Verify that emulate works for a simple function."""
    def add(a: int, b: int) -> int:
        """Add two numbers together."""
        return emulate()
    
    result = add(2, 3)
    assert result == 5

if __name__ == "__main__":
    pytest.main([__file__])
