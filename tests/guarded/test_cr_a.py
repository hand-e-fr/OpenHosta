"""Tests for CR-A: CastingResult factories, exec security, collections cache, scalar robustness, GuardedBool failure."""

import pytest

from openhosta.guarded.defaults import ALLOW_CODE_EXECUTION
from openhosta.guarded.primitives import CastingResult
from openhosta.guarded.subclassablecallables import _SAFE_BUILTINS, GuardedCode
from openhosta.guarded.subclassablecollections import (
    GuardedDict,
    GuardedList,
    GuardedSet,
)
from openhosta.guarded.subclassablescalars import GuardedInt
from openhosta.guarded.subclassablewithproxy import GuardedBool


class TestCastingResultFactories:
    """CR-01: CastingResult.ok() and CastingResult.failure() class methods."""

    def test_ok_returns_success_result(self):
        result = CastingResult.ok(42, confidence=1.0)
        assert result.success is True
        assert result.data == 42
        assert result.uncertainty == 0.0

    def test_ok_default_confidence(self):
        result = CastingResult.ok("hello")
        assert result.success is True
        assert result.uncertainty == 0.0
        assert result.abstraction == "native"

    def test_ok_custom_confidence(self):
        result = CastingResult.ok(3.14, confidence=0.8)
        assert result.success is True
        assert abs(result.uncertainty - 0.2) < 1e-9

    def test_ok_custom_abstraction(self):
        result = CastingResult.ok(1, confidence=0.9, abstraction="heuristic")
        assert result.abstraction == "heuristic"

    def test_failure_returns_failed_result(self):
        result = CastingResult.failure("bad input", confidence=0.0, error_message="invalid")
        assert result.success is False
        assert result.data is None
        assert result.uncertainty == 1.0
        assert result.error_message == "invalid"

    def test_failure_default_confidence(self):
        result = CastingResult.failure(None)
        assert result.success is False
        assert result.uncertainty == 1.0
        assert result.abstraction == "failed"

    def test_failure_custom_confidence(self):
        result = CastingResult.failure("x", confidence=0.5, error_message="partial")
        assert result.success is False
        assert abs(result.uncertainty - 0.5) < 1e-9

    def test_failure_custom_abstraction(self):
        result = CastingResult.failure(
            "x", confidence=0.0, abstraction="semantic"
        )
        assert result.abstraction == "semantic"


class TestExecSecurity:
    """CR-02: exec() security with ALLOW_CODE_EXECUTION and _SAFE_BUILTINS."""

    def test_safe_builtins_defined(self):
        assert isinstance(_SAFE_BUILTINS, dict)
        assert "__name__" in _SAFE_BUILTINS
        assert _SAFE_BUILTINS["__name__"] == "__guarded__"
        for name in ("abs", "bool", "dict", "float", "int", "len", "list",
                      "min", "max", "set", "str", "tuple", "type"):
            assert name in _SAFE_BUILTINS

    def test_safe_builtins_no_dangerous(self):
        for dangerous in ("__import__", "eval", "exec", "open", "compile"):
            assert dangerous not in _SAFE_BUILTINS

    def test_allow_code_execution_flag_exists(self):
        assert isinstance(ALLOW_CODE_EXECUTION, bool)

    def test_code_exec_disabled_raises(self, monkeypatch):
        """When ALLOW_CODE_EXECUTION is False, exec raises RuntimeError."""
        import openhosta.guarded.subclassablecallables as mod

        monkeypatch.setattr(mod, "ALLOW_CODE_EXECUTION", False)

        source = "def f(): return 1"
        with pytest.raises(RuntimeError, match="Code execution disabled"):
            GuardedCode._parse_heuristic(source)

    def test_code_exec_enabled_works(self, monkeypatch):
        """When ALLOW_CODE_EXECUTION is True, exec works."""
        import openhosta.guarded.subclassablecallables as mod

        monkeypatch.setattr(mod, "ALLOW_CODE_EXECUTION", True)

        source = "def add(a, b): return a + b"
        result = GuardedCode._parse_heuristic(source)
        assert result[0] < 1.0  # Should succeed
        assert callable(result[1])
        assert result[1](3, 4) == 7


class TestCollectionsCache:
    """CR-03: weak-key caching of parameterized collection classes."""

    def test_list_cache_returns_same_class(self):
        from openhosta.guarded.subclassablescalars import GuardedInt

        cls_a = GuardedList[GuardedInt]
        cls_b = GuardedList[GuardedInt]
        assert cls_a is cls_b

    def test_set_cache_returns_same_class(self):
        from openhosta.guarded.subclassablescalars import GuardedFloat

        cls_a = GuardedSet[GuardedFloat]
        cls_b = GuardedSet[GuardedFloat]
        assert cls_a is cls_b

    def test_dict_cache_returns_same_class(self):
        from openhosta.guarded.subclassablescalars import GuardedInt, GuardedUtf8

        cls_a = GuardedDict[GuardedUtf8, GuardedInt]
        cls_b = GuardedDict[GuardedUtf8, GuardedInt]
        assert cls_a is cls_b

    def test_different_params_different_classes(self):
        from openhosta.guarded.subclassablescalars import GuardedInt, GuardedUtf8

        cls_a = GuardedList[GuardedInt]
        cls_b = GuardedList[GuardedUtf8]
        assert cls_a is not cls_b


class TestScalarRobustness:
    """CR-04: isnumeric() replaced with regex to avoid Unicode crash."""

    def test_unicode_half_rejected_native(self):
        result = GuardedInt._parse_native("½")
        # Should not crash and should return high uncertainty (not match)
        assert result[0] == 1.0  # Tolerance.ANYTHING

    def test_unicode_circled_digit_rejected_native(self):
        result = GuardedInt._parse_native("②")
        assert result[0] == 1.0

    def test_negative_int_accepted_native(self):
        result = GuardedInt._parse_native("-42")
        assert result[0] == 0.0  # STRICT
        assert result[1] == -42

    def test_positive_int_accepted_native(self):
        result = GuardedInt._parse_native("42")
        assert result[0] == 0.0
        assert result[1] == 42


class TestGuardedBoolFailure:
    """CR-04: GuardedBool reports non-boolean error."""

    def test_non_boolean_has_error_message(self):
        result = GuardedBool._parse_heuristic("maybe")
        # uncertainty 0.5 with error message
        assert result[2] is not None
        assert "non-boolean" in result[2]

    def test_known_true_still_succeeds(self):
        result = GuardedBool._parse_heuristic("yes")
        assert result[0] == 0.0
        assert result[1] is True

    def test_known_false_still_succeeds(self):
        result = GuardedBool._parse_heuristic("no")
        assert result[0] == 0.0
        assert result[1] is False
