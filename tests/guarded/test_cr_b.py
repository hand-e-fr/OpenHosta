"""Tests for CR-B: ProxyWrapper dunders, GuardConfig, SemanticBackend, guard/unguard API."""

from dataclasses import FrozenInstanceError
from typing import Annotated

import pytest

from openhosta.guarded.api import guard, unguard
from openhosta.guarded.constants import Tolerance
from openhosta.guarded.primitives import CastingResult, GuardConfig, ProxyWrapper
from openhosta.guarded.resolver import TypeResolver, register_semantic_backend
from openhosta.guarded.semantic import LlmiSemanticBackend
from openhosta.guarded.subclassablewithproxy import GuardedBool

# ---- CR-05: ProxyWrapper dunders ----


class TestProxyWrapperUnwrap:
    def test_unwrap_proxy_returns_python_value(self):
        b = GuardedBool("yes")
        assert ProxyWrapper._unwrap(b) is True

    def test_unwrap_native_returns_identity(self):
        assert ProxyWrapper._unwrap(42) == 42
        assert ProxyWrapper._unwrap("hello") == "hello"

    def test_unwrap_nested_proxy(self):
        b1 = GuardedBool("yes")
        b2 = GuardedBool("no")
        assert ProxyWrapper._unwrap(b1) is True
        assert ProxyWrapper._unwrap(b2) is False


class TestProxyWrapperArithmetic:
    """Arithmetic dunder delegation on ProxyWrapper types."""

    def test_add(self):
        b = GuardedBool("yes")
        assert b + 1 == 2

    def test_sub(self):
        b = GuardedBool("yes")
        assert b - 0 == 1

    def test_mul(self):
        b = GuardedBool("yes")
        assert b * 3 == 3

    def test_truediv(self):
        b = GuardedBool("yes")
        assert b / 2 == 0.5

    def test_floordiv(self):
        b = GuardedBool("yes")
        assert b // 1 == 1

    def test_mod(self):
        b = GuardedBool("yes")
        assert b % 2 == 1

    def test_pow(self):
        b = GuardedBool("yes")
        assert b ** 2 == 1


class TestProxyWrapperOrdering:
    """Ordering dunder delegation."""

    def test_lt(self):
        b_true = GuardedBool("yes")
        b_false = GuardedBool("no")
        # bool True == 1, False == 0
        assert not (b_true < b_false)
        assert b_false < b_true

    def test_le(self):
        b_true = GuardedBool("yes")
        b_false = GuardedBool("no")
        assert b_false <= b_true
        assert b_true <= b_true

    def test_gt(self):
        b_true = GuardedBool("yes")
        b_false = GuardedBool("no")
        assert b_true > b_false
        assert not (b_false > b_true)

    def test_ge(self):
        b_true = GuardedBool("yes")
        b_false = GuardedBool("no")
        assert b_true >= b_false
        assert b_false >= b_false


class TestProxyWrapperConversion:
    """Conversion dunder delegation."""

    def test_int(self):
        b = GuardedBool("yes")
        assert int(b) == 1

    def test_float(self):
        b = GuardedBool("yes")
        assert float(b) == 1.0

    def test_bool(self):
        b_true = GuardedBool("yes")
        b_false = GuardedBool("no")
        assert bool(b_true) is True
        assert bool(b_false) is False

    def test_complex(self):
        b = GuardedBool("yes")
        assert complex(b) == 1 + 0j


class TestProxyWrapperBitwise:
    """Bitwise dunder delegation."""

    def test_and(self):
        b1 = GuardedBool("yes")
        b2 = GuardedBool("yes")
        assert b1 & b2 == 1

    def test_or(self):
        b1 = GuardedBool("yes")
        b2 = GuardedBool("no")
        assert b1 | b2 == 1

    def test_xor(self):
        b1 = GuardedBool("yes")
        b2 = GuardedBool("no")
        assert b1 ^ b2 == 1

    def test_lshift(self):
        b = GuardedBool("yes")
        assert b << 2 == 4

    def test_rshift(self):
        # True == 1, 1 >> 1 == 0
        b = GuardedBool("yes")
        assert b >> 1 == 0


class TestProxyWrapperNegationAbs:
    """Negation and abs dunder delegation."""

    def test_neg(self):
        b = GuardedBool("yes")
        assert -b == -1

    def test_pos(self):
        b = GuardedBool("yes")
        assert +b == 1

    def test_abs(self):
        b = GuardedBool("yes")
        assert abs(b) == 1


class TestProxyWrapperWithOtherProxy:
    """Operations between two ProxyWrapper instances."""

    def test_add_two_proxies(self):
        b1 = GuardedBool("yes")
        b2 = GuardedBool("yes")
        assert b1 + b2 == 2

    def test_mul_two_proxies(self):
        b1 = GuardedBool("yes")
        b2 = GuardedBool("no")
        assert b1 * b2 == 0

    def test_and_two_proxies(self):
        b1 = GuardedBool("yes")
        b2 = GuardedBool("no")
        assert b1 & b2 == 0


# ---- CR-06: GuardConfig + Annotated wiring ----


class TestGuardConfig:
    def test_default_values(self):
        gc = GuardConfig()
        assert gc.tolerance == 1.0
        assert gc.semantic_fallback is None
        assert gc.retries == 3

    def test_custom_values(self):
        gc = GuardConfig(tolerance=0.05, semantic_fallback="llm", retries=5)
        assert gc.tolerance == 0.05
        assert gc.semantic_fallback == "llm"
        assert gc.retries == 5

    def test_frozen(self):
        gc = GuardConfig(tolerance=0.5)
        with pytest.raises(FrozenInstanceError):
            gc.tolerance = 0.1  # type: ignore


class TestAnnotatedGuardConfig:
    def test_annotated_int_with_config(self):
        ann_type = Annotated[int, GuardConfig(tolerance=0.0)]
        resolved = TypeResolver.resolve(ann_type)
        assert resolved._tolerance == 0.0

    def test_annotated_str_with_config(self):
        ann_type = Annotated[str, GuardConfig(tolerance=0.5, retries=10)]
        resolved = TypeResolver.resolve(ann_type)
        assert resolved._tolerance == 0.5

    def test_annotated_plain_int_no_config(self):
        ann_type = Annotated[int, "some_metadata"]
        resolved = TypeResolver.resolve(ann_type)
        # Falls through to GuardedInt default tolerance
        from openhosta.guarded.subclassablescalars import GuardedInt
        assert resolved._tolerance == GuardedInt._tolerance

    def test_annotated_rejects_above_tolerance(self):
        """When tolerance is 0.0 (STRICT), heuristic-cleaned values should fail."""
        ann_type = Annotated[int, GuardConfig(tolerance=Tolerance.STRICT)]
        resolved = TypeResolver.resolve(ann_type)
        # Native int should pass
        result = resolved.attempt(42)
        assert result.success is True
        # "42 ans" requires heuristic cleaning, which exceeds STRICT tolerance
        result2 = resolved.attempt("42 ans")
        assert result2.success is False


# ---- CR-07: SemanticBackend ----


class TestSemanticBackendProtocol:
    def test_register_and_retrieve(self):
        class DummyBackend:
            def resolve(self, value: str, target_type: type) -> CastingResult:
                return CastingResult.ok("resolved", confidence=0.9)

        register_semantic_backend(DummyBackend())
        from openhosta.guarded import resolver as _resolver
        assert _resolver._SEMANTIC_BACKEND is not None

    def test_llmi_semantic_backend_returns_failure(self):
        backend = LlmiSemanticBackend()
        result = backend.resolve("hello", int)
        assert result.success is False
        assert "Semantic backend not wired" in (result.error_message or "")

    def test_llmi_semantic_backend_satisfies_protocol(self):
        backend = LlmiSemanticBackend()
        assert hasattr(backend, "resolve")
        result = backend.resolve("test", str)
        assert isinstance(result, CastingResult)


# ---- CR-08: guard / unguard API ----


class TestGuard:
    def test_guard_int(self):
        result = guard(42, int)
        assert result.unwrap() == 42
        assert hasattr(result, "uncertainty")

    def test_guard_int_from_string(self):
        result = guard("42", int)
        assert result.unwrap() == 42

    def test_guard_str(self):
        result = guard("hello", str)
        assert result.unwrap() == "hello"

    def test_guard_float(self):
        result = guard(3.14, float)
        assert result.unwrap() == pytest.approx(3.14)

    def test_guard_bool(self):
        result = guard(True, bool)
        assert result.unwrap() is True

    def test_guard_default_target(self):
        result = guard(99)
        assert result.unwrap() == 99

    def test_guard_invalid_raises(self):
        with pytest.raises(ValueError):
            guard("not_a_number", int)


class TestUnguard:
    def test_unguard_int(self):
        g = guard(42, int)
        assert unguard(g) == 42

    def test_unguard_str(self):
        g = guard("hello", str)
        assert unguard(g) == "hello"

    def test_unguard_float(self):
        g = guard(3.14, float)
        assert unguard(g) == pytest.approx(3.14)

    def test_unguard_bool(self):
        g = guard(True, bool)
        assert unguard(g) is True

    def test_unguard_round_trip(self):
        original = "test_value"
        guarded = guard(original, str)
        recovered = unguard(guarded)
        assert recovered == original
        assert type(recovered) is str


class TestGuardUnguardIntegration:
    def test_guard_annotated_type(self):
        """guard with Annotated type carrying GuardConfig."""
        ann = Annotated[int, GuardConfig(tolerance=Tolerance.TYPE_COMPLIANT)]
        result = guard("42", ann)
        assert result.unwrap() == 42

    def test_guard_unguard_list(self):
        result = guard("[1, 2, 3]", list)
        unwrapped = unguard(result)
        assert unwrapped == [1, 2, 3]

    def test_guard_unguard_dict(self):
        result = guard('{"a": 1, "b": 2}', dict)
        unwrapped = unguard(result)
        assert unwrapped == {"a": 1, "b": 2}
