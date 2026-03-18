import pytest
from enum import auto

from OpenHosta.guarded import GuardedEnum
from OpenHosta.core.meta_prompt import EMULATE_META_PROMPT, USER_CALL_META_PROMPT
from OpenHosta.core.analizer import hosta_analyze, encode_function # NOTE: analysis will be updated

class MyEnum(GuardedEnum):
    ACTION_A = auto()
    ACTION_B = auto()

# We will test dict[tuple, dict[MyEnum, list[str]]]
def dummy_recursive_function(
    data: dict[tuple, dict[MyEnum, list[str]]]
) -> tuple[MyEnum, str]:
    """
    Dummy recursive function for testing.
    """
    pass

def test_type_resolution_in_prompt():
    
    # 1. Analyze the function (returns the new AnalyzedFunction object)
    analyse = hosta_analyze(function_pointer=dummy_recursive_function)
    
    # 2. Encode to strings based on types
    encoded_data = encode_function(analyse)
    
    # 3. Render the meta prompt
    # In the refactored code, we want to ensure the meta-prompt explicitly contains
    # a description of the recursive types and the Enum
    
    system_prompt = EMULATE_META_PROMPT.render(encoded_data)
    
    # Assertions
    # We checking that important words appear in the rendered templates
    
    # Expected fragments in the system prompt based on Guarded resolution:
    # 1. Return type explicitly mentioned
    assert "a tuple of (a value from MyEnum enum, a string)" in system_prompt.lower() or "tuple" in system_prompt.lower()
    
    # 2. Argument type resolution should be present
    assert "dictionary" in system_prompt.lower()
    assert "tuple" in system_prompt.lower()
    assert "myenum" in system_prompt.lower()
    assert "list" in system_prompt.lower()

    # 3. Enum members should be exposed in the prompt constraint
    # This might require some tweaking depending on how TypeResolver ultimately injects JSON schemas or descriptions.
    assert "action_a" in system_prompt.lower()
    assert "action_b" in system_prompt.lower()

if __name__ == "__main__":
    pytest.main([__file__])
