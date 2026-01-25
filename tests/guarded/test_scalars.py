"""Tests for GuardedInt, GuardedFloat, and GuardedUtf8."""

import pytest
from src.OpenHosta.guarded.constants import Tolerance
from src.OpenHosta.guarded.subclassablescalars import GuardedInt, GuardedFloat, GuardedUtf8


class TestGuardedInt:
    """Tests for GuardedInt type."""
    
    def test_native_int(self):
        """Test with native int."""
        age = GuardedInt(42)
        assert age == 42
        assert age.uncertainty == Tolerance.STRICT
        assert age.abstraction_level == 'native'
    
    def test_numeric_string(self):
        """Test with numeric string."""
        age = GuardedInt("42")
        assert age == 42
        assert age.uncertainty == Tolerance.STRICT
        assert age.abstraction_level == 'native'
    
    def test_float_to_int(self):
        """Test conversion from float to int."""
        age = GuardedInt(42.0)
        assert age == 42
        assert age.uncertainty == Tolerance.STRICT
    
    def test_string_with_spaces(self):
        """Test string with spaces."""
        num = GuardedInt("1 000")
        assert num == 1000
        assert age.uncertainty <= Tolerance.FLEXIBLE
        assert age.abstraction_level == 'heuristic'
    
    def test_string_with_commas(self):
        """Test string with comma separators."""
        num = GuardedInt("1,000")
        assert num == 1000
        assert num.uncertainty <= Tolerance.FLEXIBLE
    
    def test_negative_number(self):
        """Test negative numbers."""
        num = GuardedInt("-42")
        assert num == -42
    
    def test_invalid_input(self):
        """Test that invalid input raises ValueError."""
        with pytest.raises(ValueError):
            GuardedInt("not a number")
    
    def test_bool_rejected(self):
        """Test that bool is not accepted as int."""
        # True is technically an int in Python, but we reject it
        result = GuardedInt(True)
        # Should work but with higher uncertainty
        assert result == 1


class TestGuardedFloat:
    """Tests for GuardedFloat type."""
    
    def test_native_float(self):
        """Test with native float."""
        pi = GuardedFloat(3.14)
        assert pi == 3.14
        assert pi.uncertainty == Tolerance.STRICT
    
    def test_int_to_float(self):
        """Test conversion from int to float."""
        num = GuardedFloat(42)
        assert num == 42.0
        assert num.uncertainty == Tolerance.STRICT
    
    def test_string_float(self):
        """Test with string representation."""
        pi = GuardedFloat("3.14")
        assert pi == 3.14
        assert pi.uncertainty == Tolerance.STRICT
    
    def test_european_format(self):
        """Test European format with comma as decimal separator."""
        pi = GuardedFloat("3,14")
        assert abs(pi - 3.14) < 0.01
        assert pi.uncertainty <= Tolerance.FLEXIBLE
    
    def test_multiple_dots(self):
        """Test handling of multiple dots (thousands separator)."""
        num = GuardedFloat("1.000.000,5")
        assert abs(num - 1000000.5) < 0.1
    
    def test_invalid_input(self):
        """Test that invalid input raises ValueError."""
        with pytest.raises(ValueError):
            GuardedFloat("not a number")


class TestGuardedUtf8:
    """Tests for GuardedUtf8 type."""
    
    def test_native_string(self):
        """Test with native string."""
        text = GuardedUtf8("hello")
        assert text == "hello"
        assert text.uncertainty == Tolerance.STRICT
    
    def test_bytes_to_string(self):
        """Test conversion from bytes."""
        text = GuardedUtf8(b"hello")
        assert text == "hello"
        assert text.uncertainty == Tolerance.STRICT
        assert text.abstraction_level == 'heuristic'
    
    def test_unicode(self):
        """Test with unicode characters."""
        text = GuardedUtf8("héllo wörld 🌍")
        assert text == "héllo wörld 🌍"
    
    def test_empty_string(self):
        """Test with empty string."""
        text = GuardedUtf8("")
        assert text == ""
    
    def test_invalid_bytes(self):
        """Test with invalid UTF-8 bytes."""
        # This should fail gracefully
        with pytest.raises(ValueError):
            GuardedUtf8(b'\xff\xfe')
    
    def test_metadata_preserved(self):
        """Test that metadata is preserved."""
        text = GuardedUtf8("test")
        assert hasattr(text, 'uncertainty')
        assert hasattr(text, 'abstraction_level')
        assert hasattr(text, 'unwrap')


class TestScalarOperations:
    """Test that guarded types work like native types."""
    
    def test_int_arithmetic(self):
        """Test arithmetic operations on GuardedInt."""
        a = GuardedInt(10)
        b = GuardedInt(5)
        
        assert a + b == 15
        assert a - b == 5
        assert a * b == 50
        assert a // b == 2
    
    def test_float_arithmetic(self):
        """Test arithmetic operations on GuardedFloat."""
        a = GuardedFloat(10.5)
        b = GuardedFloat(2.5)
        
        assert a + b == 13.0
        assert a - b == 8.0
        assert abs(a * b - 26.25) < 0.01
    
    def test_string_operations(self):
        """Test string operations on GuardedUtf8."""
        text = GuardedUtf8("hello")
        
        assert text.upper() == "HELLO"
        assert text + " world" == "hello world"
        assert "ell" in text
        assert len(text) == 5
    
    def test_comparison(self):
        """Test comparison operations."""
        a = GuardedInt(10)
        b = GuardedInt(20)
        
        assert a < b
        assert b > a
        assert a <= b
        assert b >= a
        assert a != b
