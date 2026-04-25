import pytest
from OpenHosta import emulate, emulate_async, Guarded, conversation, readable, markdown
from OpenHosta.guarded import GuardedInt, GuardedList, GuardedUtf8
import asyncio

def test_inspection_guarded_int(capsys):
    """Test inspection functions with Guarded[int]."""
    def get_age(name: str) -> Guarded[int]:
        """Return the age of the person."""
        return emulate()

    age = get_age("John was born in 1990 and we are in 2026")
    
    # Check type (should be GuardedInt because of automatic resolution)
    assert isinstance(age, GuardedInt)
    assert int(age) > 0

    # Test conversation()
    conversation(age)
    captured = capsys.readouterr()
    assert "Model" in captured.out
    assert "System prompt" in captured.out
    assert "User prompt" in captured.out
    assert "name='John was born in 1990 and we are in 2026'" in captured.out
    assert "get_age(name)" in captured.out

    # Test readable()
    r = readable(age)
    assert r == str(int(age))
    
    # Test stability
    age_copy = GuardedInt(r)
    assert age_copy == age

def test_inspection_guarded_list(capsys):
    """Test inspection functions with Guarded[list[int]]."""
    def get_scores(name: str) -> Guarded[list[int]]:
        """Return a list of 3 scores."""
        return emulate()

    scores = get_scores("John played a very hard game yesterday, he scored 10, then 12, then 15 points")
    assert isinstance(scores, GuardedList)
    assert len(scores) == 3

    # Test conversation()
    conversation(scores)
    captured = capsys.readouterr()
    assert "Model" in captured.out
    assert "name='John played a very hard game yesterday, he scored 10, then 12, then 15 points'" in captured.out
    assert "get_scores(name)" in captured.out

    # Test readable() - should be pretty-printed JSON
    r = readable(scores)
    assert "[" in r
    assert "]" in r
    
    # Test stability
    scores_copy = GuardedList(r)
    assert scores_copy == scores

def test_inspection_markdown():
    """Test markdown formatting."""
    def get_bio(name: str) -> Guarded[str]:
        """Return a short bio."""
        return emulate()

    bio = get_bio("John")
    m = markdown(bio)
    
    # Since it's a string, if it has newlines it should be in a block
    if "\n" in str(bio):
        assert m.startswith("```python")
        assert m.endswith("```")
    else:
        assert m == str(bio)

@pytest.mark.asyncio
async def test_inspection_async():
    """Test inspection with emulate_async and Guarded[T]."""
    async def get_val() -> Guarded[int]:
        """Return 42."""
        return await emulate_async()

    val = await get_val()
    assert isinstance(val, GuardedInt)
    assert val == 42
    
    # conversation() should still work
    import io
    from contextlib import redirect_stdout
    f = io.StringIO()
    with redirect_stdout(f):
        conversation(val)
    out = f.getvalue()
    assert "Model" in out

def test_inspection_stability_complex():
    """Verify stability with complex input (artifacts)."""
    # Simulate a response with artifacts that gets cleaned
    llm_out = "[10, 20, 30] # These are the results"
    
    # Manual creation to verify the logic we want to document
    g_list = GuardedList(llm_out)
    assert g_list == [10, 20, 30]
    
    r = readable(g_list)
    # readable() should return just the JSON list, no comments
    assert "#" not in r
    
    # Stability check
    g_list_2 = GuardedList(r)
    assert g_list_2 == g_list
