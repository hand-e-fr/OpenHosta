"""Tests for GuardedCode and GuardedCallable types."""

import pytest
import types
from OpenHosta.guarded.subclassablecallables import GuardedCode
from OpenHosta.guarded.constants import Tolerance


class TestGuardedCode:
    """Tests for GuardedCode type."""
    
    def test_native_function(self):
        """Test with native function."""
        def my_func(x):
            return x + 1
        
        code = GuardedCode(my_func)
        assert code(5) == 6
        assert code.uncertainty == Tolerance.STRICT
        assert code.abstraction_level == 'native'
    
    def test_lambda(self):
        """Test with lambda."""
        code = GuardedCode(lambda x: x * 2)
        assert code(10) == 20
        assert code.uncertainty == Tolerance.STRICT
    
    def test_source_code_heuristic(self):
        """Test with function source code string."""
        source = "def add(a, b): return a + b"
        code = GuardedCode(source)
        
        # Should be compiled and callable
        assert code(2, 3) == 5
        assert code.uncertainty == Tolerance.TYPE_COMPLIANT
        assert code.abstraction_level == 'heuristic'
    
    def test_markdown_code_block(self):
        """Test with markdown code block."""
        source = "```python\ndef multiply(a, b): return a * b\n```"
        code = GuardedCode(source)
        
        assert code(3, 4) == 12
        assert code.uncertainty == Tolerance.TYPE_COMPLIANT
    
    def test_invalid_syntax(self):
        """Test with invalid syntax."""
        source = "def incomplete("
        # Should return UncertaintyLevel(Tolerance.ANYTHING) and the original value
        # But wait, GuardedPrimitive(value) calls _parse_native then _parse_heuristic
        # if both return ANYTHING, it raises ValueError if tolerance is strict.
        # By default tolerance is TYPE_COMPLIANT (0.99)
        with pytest.raises(ValueError):
             # Since it's invalid it will fail to be a callable
             GuardedCode(source)

    def test_empty_string(self):
        """Test with empty string."""
        with pytest.raises(ValueError):
            GuardedCode("")

    def test_callable_instance(self):
        """Test with class instance that is callable."""
        class Adder:
            def __call__(self, x, y):
                return x + y
        
        code = GuardedCode(Adder())
        assert code(1, 1) == 2
        assert code.uncertainty == Tolerance.STRICT
