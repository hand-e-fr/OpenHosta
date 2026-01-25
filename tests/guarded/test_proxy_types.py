"""Tests for ProxyWrapper types (GuardedBool, GuardedNone, etc.)."""

import pytest
from OpenHosta.guarded.constants import Tolerance
from OpenHosta.guarded.subclassablewithproxy import (
    GuardedBool, GuardedNone, GuardedAny
)


class TestGuardedBool:
    """Tests for GuardedBool type."""
    
    def test_native_bool(self):
        """Test with native bool."""
        b = GuardedBool(True)
        assert b.unwrap() == True
        assert b.uncertainty == Tolerance.STRICT
    
    def test_string_yes(self):
        """Test with 'yes' string."""
        b = GuardedBool("yes")
        assert b.unwrap() == True
        assert b.uncertainty == Tolerance.STRICT
    
    def test_string_no(self):
        """Test with 'no' string."""
        b = GuardedBool("no")
        assert b.unwrap() == False
    
    def test_french_oui(self):
        """Test with French 'oui'."""
        b = GuardedBool("oui")
        assert b.unwrap() == True
    
    def test_french_non(self):
        """Test with French 'non'."""
        b = GuardedBool("non")
        assert b.unwrap() == False
    
    def test_case_insensitive(self):
        """Test case insensitivity."""
        b1 = GuardedBool("YES")
        b2 = GuardedBool("No")
        assert b1.unwrap() == True
        assert b2.unwrap() == False
    
    def test_numeric_conversion(self):
        """Test numeric to bool conversion."""
        b1 = GuardedBool(1)
        b2 = GuardedBool(0)
        assert b1.unwrap() == True
        assert b2.unwrap() == False
    
    def test_bool_method(self):
        """Test __bool__ method."""
        b1 = GuardedBool("yes")
        b2 = GuardedBool("no")
        
        if b1:
            assert True
        else:
            assert False, "Should be truthy"
        
        if not b2:
            assert True
        else:
            assert False, "Should be falsy"
    
    def test_unwrap_method(self):
        """Test unwrap returns native bool."""
        b = GuardedBool("yes")
        unwrapped = b.unwrap()
        assert isinstance(unwrapped, bool)
        assert unwrapped is True


class TestGuardedNone:
    """Tests for GuardedNone type."""
    
    def test_native_none(self):
        """Test with native None."""
        n = GuardedNone(None)
        assert n.unwrap() is None
        assert n.uncertainty == Tolerance.STRICT
    
    def test_string_none(self):
        """Test with 'None' string."""
        n = GuardedNone("None")
        assert n.unwrap() is None
        assert n.uncertainty <= Tolerance.PRECISE
    
    def test_string_null(self):
        """Test with 'null' string."""
        n = GuardedNone("null")
        assert n.unwrap() is None
    
    def test_string_nothing(self):
        """Test with 'nothing' string."""
        n = GuardedNone("nothing")
        assert n.unwrap() is None
    
    def test_french_rien(self):
        """Test with French 'rien'."""
        n = GuardedNone("rien")
        assert n.unwrap() is None
    
    def test_case_insensitive(self):
        """Test case insensitivity."""
        n1 = GuardedNone("NULL")
        n2 = GuardedNone("None")
        assert n1.unwrap() is None
        assert n2.unwrap() is None
    
    def test_repr(self):
        """Test string representation."""
        n = GuardedNone(None)
        assert repr(n) == "None"


class TestGuardedAny:
    """Tests for GuardedAny type."""
    
    def test_accepts_anything(self):
        """Test that GuardedAny accepts any value."""
        values = [42, "hello", [1, 2, 3], {"a": 1}, None, True]
        
        for val in values:
            a = GuardedAny(val)
            assert a.unwrap() == val
            assert a.uncertainty == Tolerance.STRICT
    
    def test_tolerance(self):
        """Test that GuardedAny has TYPE_COMPLIANT tolerance."""
        a = GuardedAny("anything")
        assert a._tolerance == Tolerance.TYPE_COMPLIANT


class TestProxyWrapperBehavior:
    """Test ProxyWrapper base class behavior."""
    
    def test_equality(self):
        """Test equality comparison."""
        b1 = GuardedBool("yes")
        b2 = GuardedBool(True)
        b3 = GuardedBool("no")
        
        assert b1 == b2
        assert b1 != b3
    
    def test_equality_with_native(self):
        """Test equality with native types."""
        b = GuardedBool("yes")
        assert b == True
        assert b != False
    
    def test_hash(self):
        """Test that proxy types are hashable."""
        b1 = GuardedBool("yes")
        b2 = GuardedBool(True)
        
        # Should be hashable
        s = {b1, b2}
        assert len(s) == 1  # Same hash
    
    def test_repr(self):
        """Test string representation."""
        b = GuardedBool(True)
        n = GuardedNone(None)
        
        assert "True" in repr(b)
        assert "None" in repr(n)
    
    def test_str(self):
        """Test str conversion."""
        b = GuardedBool(True)
        assert str(b) == "True"
    
    def test_not_instance_of_native(self):
        """Test that proxy is not instance of native type."""
        b = GuardedBool(True)
        n = GuardedNone(None)
        
        # These should be False because it's a proxy
        assert not isinstance(b, bool)
        assert not isinstance(n, type(None))
        
        # But unwrap should give native type
        assert isinstance(b.unwrap(), bool)
        assert n.unwrap() is None
