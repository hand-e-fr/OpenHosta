"""
Tests for Tolerance constants in OpenHosta.semantics.constants.
Verifies the tolerance level values and describe() method.
"""
import pytest


class TestToleranceConstants:
    """Tests for Tolerance constant values."""
    
    def test_tolerance_strict_value(self):
        """STRICT tolerance should be 0.0 (exact match)."""
        from OpenHosta.guarded.constants import Tolerance
        assert Tolerance.STRICT == 0.0
    
    def test_tolerance_precise_value(self):
        """PRECISE tolerance should be 0.05."""
        from OpenHosta.guarded.constants import Tolerance
        assert Tolerance.PRECISE == 0.05
    
    def test_tolerance_flexible_value(self):
        """FLEXIBLE tolerance (default) should be 0.15."""
        from OpenHosta.guarded.constants import Tolerance
        assert Tolerance.FLEXIBLE == 0.15
    
    def test_tolerance_creative_value(self):
        """CREATIVE tolerance should be 0.30."""
        from OpenHosta.guarded.constants import Tolerance
        assert Tolerance.CREATIVE == 0.30
    
    def test_tolerance_ordering(self):
        """Tolerance levels should be in ascending order."""
        from OpenHosta.guarded.constants import Tolerance
        assert Tolerance.STRICT < Tolerance.PRECISE < Tolerance.FLEXIBLE < Tolerance.CREATIVE


class TestToleranceDescribe:
    """Tests for Tolerance.describe() method."""
    
    def test_describe_strict(self):
        """Should describe STRICT level."""
        from OpenHosta.guarded.constants import Tolerance
        desc = Tolerance.describe(Tolerance.STRICT)
        assert "STRICT" in desc
    
    def test_describe_precise(self):
        """Should describe PRECISE level."""
        from OpenHosta.guarded.constants import Tolerance
        desc = Tolerance.describe(Tolerance.PRECISE)
        assert "PRECISE" in desc
    
    def test_describe_flexible(self):
        """Should describe FLEXIBLE level."""
        from OpenHosta.guarded.constants import Tolerance
        desc = Tolerance.describe(Tolerance.FLEXIBLE)
        assert "FLEXIBLE" in desc
    
    def test_describe_creative(self):
        """Should describe values above FLEXIBLE as CREATIVE."""
        from OpenHosta.guarded.constants import Tolerance
        desc = Tolerance.describe(Tolerance.CREATIVE)
        assert "CREATIVE" in desc
    
    def test_describe_intermediate_value(self):
        """Should describe intermediate values correctly."""
        from OpenHosta.guarded.constants import Tolerance
        # Value between PRECISE and FLEXIBLE should be FLEXIBLE
        desc = Tolerance.describe(0.10)
        assert "FLEXIBLE" in desc
