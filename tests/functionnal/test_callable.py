import pytest
from OpenHosta.guarded import GuardedCallable
from OpenHosta import emulate

def generate_calculator() -> GuardedCallable:
    """
    Create a python function that takes two numbers and returns their sum.
    The function must be named 'add'.
    """
    return emulate()

@pytest.mark.asyncio
async def test_callable_returns_guarded_and_prints_source():
    # Emulate should return a GuardedCallable wrapper
    result = generate_calculator()
    
    # We should be able to call it
    assert result(2, 3) == 5
    
    # And we should be able to print its source code
    source = str(result)
    assert "def add" in source
    assert "return" in source
