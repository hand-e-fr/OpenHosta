import pytest
from OpenHosta import ask, emulate
from OpenHosta.semantics import SemanticDict
from dotenv import load_dotenv

load_dotenv()

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

def test_smoke_semantics():
    """Verify that SemanticDict works for basic fuzzy lookup."""
    # Try to use a base model from env if available to avoid 404
    import os
    embedding_model = os.getenv("OPENHOSTA_TEST_EMBEDDING_MODEL", "text-embedding-3-small")
    
    try:
        sd = SemanticDict(
            {"apple": "fruit", "carrot": "vegetable"},
        )
        # Fuzzy lookup for something close to apple
        result = sd["red fruit"]
        assert result == "fruit"
    except Exception as e:
        if "404" in str(e) and "not found" in str(e):
            pytest.skip(f"Embedding model not found: {e}")
        raise e

if __name__ == "__main__":
    pytest.main([__file__])
