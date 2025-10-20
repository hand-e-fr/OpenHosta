import pytest
import asyncio

from OpenHosta import test as oh_test
from OpenHosta import test_async as oh_test_async
    
class TestSemanticTests:
    
    def test_BasicMandatory(self):
        name = "Louis"
        if oh_test(f"Is '{name}' a name ?"):
            result = f"Yes, {name} is a name"
        else:
            result = f"No, {name} is not a name"
        assert result.startswith("Yes"), "Louis should be recognized as a name"
        
    def test_BasicMandatoryAsync(self):
        
        async def run_test():
            name = "Louis"
            if await oh_test_async(f"Is '{name}' a name ?"):
                result = f"Yes, {name} is a name"
            else:
                result = f"No, {name} is not a name"
            return result
        
        result = asyncio.run(run_test())
        assert result.startswith("Yes"), "Louis should be recognized as a name"
    
    def test_WithDatastructures(self):
        names_1 = ["Louis", "Apple", "Marie"]
        names_2 = ["Louis", "Martin", "Marie"]
        
        if oh_test("all words are names", names_1):
            result = "All words are names"
        else:
            result = "Not all words are names"

        assert result == "Not all words are names", "All words in names_1 should be recognized as names"

        if oh_test("all words are names", names_2):
            result = "All words are names"
        else:
            result = "Not all words are names"

        assert result == "All words are names", "Not all words in names_2 should be recognized as names"
        
        
    def test_with_names_parameter(self):
        names = ["Louis", "Apple", "Marie"]
        
        if oh_test("all words are names", names=names):
            result = "All words are names"
        else:
            result = "Not all words are names"

        assert result == "Not all words are names", "All words in names should be recognized as names"