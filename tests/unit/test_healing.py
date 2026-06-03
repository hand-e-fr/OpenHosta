"""Tests for healing module — GuardConfig, HealingState, HealingHook, Healer, heal.

REQ-LEARN-001 — Auto-healing retry with adaptive backoff and guardrails
"""

from __future__ import annotations

from typing import Any

import pytest

from openhosta.agent.healing import (
    GuardConfig,
    Healer,
    HealingHook,
    HealingState,
    heal,
)

# ============================================================================
# TestGuardConfig
# ============================================================================


class TestGuardConfig:
    def test_default_values(self) -> None:
        g = GuardConfig()
        assert g.heal_retries_per_layer == 3
        assert g.max_effort_ms == -1.0
        assert g.initial_backoff_ms == 100.0
        assert g.max_backoff_ms == 5_000.0
        assert g.backoff_factor == 2.0
        assert g.fuzzy_threshold == 0.6
        assert g.layer == 0
        assert g.description == ""

    def test_derive_child_reduces_retries(self) -> None:
        g = GuardConfig(heal_retries_per_layer=5, max_effort_ms=1000.0)
        child = g.derive_child(1)
        assert child.heal_retries_per_layer == 4
        assert child.layer == 1

    def test_derive_child_reduces_time_budget(self) -> None:
        g = GuardConfig(max_effort_ms=1000.0)
        child = g.derive_child(1)
        assert child.max_effort_ms == pytest.approx(700.0)

    def test_derive_child_unlimited_time_stays_unlimited(self) -> None:
        g = GuardConfig(max_effort_ms=-1.0)
        child = g.derive_child(1)
        assert child.max_effort_ms == -1.0

    def test_derive_child_min_retries_is_one(self) -> None:
        g = GuardConfig(heal_retries_per_layer=1)
        child = g.derive_child(1)
        assert child.heal_retries_per_layer == 1

    def test_derive_child_min_effort_is_fifty(self) -> None:
        g = GuardConfig(max_effort_ms=71.0)
        child = g.derive_child(1)
        assert child.max_effort_ms == 50.0

    def test_derive_child_inherits_other_fields(self) -> None:
        g = GuardConfig(
            initial_backoff_ms=200.0,
            max_backoff_ms=8000.0,
            backoff_factor=3.0,
            fuzzy_threshold=0.8,
            description="root",
        )
        child = g.derive_child(2)
        assert child.initial_backoff_ms == 200.0
        assert child.max_backoff_ms == 8000.0
        assert child.backoff_factor == 3.0
        assert child.fuzzy_threshold == 0.8
        assert child.description == "root"


# ============================================================================
# TestHealingState
# ============================================================================


class TestHealingState:
    def test_default_values(self) -> None:
        s = HealingState()
        assert s.attempt == 0
        assert s.total_ms == 0.0
        assert s.errors == []

    def test_can_track_attempts_and_errors(self) -> None:
        s = HealingState()
        s.attempt += 1
        s.errors.append(RuntimeError("e1"))
        s.attempt += 1
        s.errors.append(ValueError("e2"))
        assert s.attempt == 2
        assert len(s.errors) == 2
        assert isinstance(s.errors[0], RuntimeError)
        assert isinstance(s.errors[1], ValueError)


# ============================================================================
# TestHealingHook
# ============================================================================


class TestHealingHook:
    def test_default_before_retry_returns_true(self) -> None:
        hook = HealingHook()
        g = GuardConfig()
        s = HealingState()
        assert hook.before_retry(g, s, RuntimeError()) is True

    def test_default_after_failure_does_not_raise(self) -> None:
        hook = HealingHook()
        g = GuardConfig()
        s = HealingState()
        hook.after_failure(g, s, RuntimeError())


class _AbortingHook(HealingHook):
    def before_retry(
        self,
        guard: GuardConfig,
        state: HealingState,
        last_error: BaseException,
    ) -> bool:
        return False


class _TrackingHook(HealingHook):
    after_called: bool = False

    def after_failure(
        self,
        guard: GuardConfig,
        state: HealingState,
        error: BaseException,
    ) -> None:
        self.after_called = True


class TestHealingHookSubclass:
    def test_subclass_can_override_before_retry_to_return_false(self) -> None:
        hook = _AbortingHook()
        assert hook.before_retry(GuardConfig(), HealingState(), RuntimeError()) is False

    def test_subclass_can_override_after_failure(self) -> None:
        hook = _TrackingHook()
        hook.after_failure(GuardConfig(), HealingState(), RuntimeError())
        assert hook.after_called is True


# ============================================================================
# TestHealerFuzzy
# ============================================================================


class TestHealerFuzzy:
    def test_exact_match(self) -> None:
        registry = {"my_func": lambda context=None: 42}
        healer = Healer(guard=GuardConfig(heal_retries_per_layer=0, max_effort_ms=-1.0), registry=registry)

        def fail() -> Any:
            raise RuntimeError("nope")

        res = healer.execute(fail, fallback_name="my_func")
        assert res.success is True
        assert res.result == 42
        assert res.fallback_name == "my_func"

    def test_case_insensitive_match(self) -> None:
        registry = {"MyFunc": lambda context=None: 99}
        healer = Healer(guard=GuardConfig(heal_retries_per_layer=0, max_effort_ms=-1.0), registry=registry)

        def fail() -> Any:
            raise RuntimeError("nope")

        res = healer.execute(fail, fallback_name="myfunc")
        assert res.success is True
        assert res.result == 99
        assert res.fallback_name == "MyFunc"

    def test_hyphen_underscore_match(self) -> None:
        registry = {"my_func": lambda context=None: 77}
        healer = Healer(guard=GuardConfig(heal_retries_per_layer=0, max_effort_ms=-1.0), registry=registry)

        def fail() -> Any:
            raise RuntimeError("nope")

        res = healer.execute(fail, fallback_name="my-func")
        assert res.success is True
        assert res.fallback_name == "my_func"

    def test_difflib_fallback(self) -> None:
        registry = {"preprocess": lambda context=None: "ok"}
        healer = Healer(
            guard=GuardConfig(heal_retries_per_layer=0, max_effort_ms=-1.0, fuzzy_threshold=0.6),
            registry=registry,
        )

        def fail() -> Any:
            raise RuntimeError("nope")

        res = healer.execute(fail, fallback_name="preproce")
        assert res.success is True
        assert res.fallback_name == "preprocess"

    def test_fuzzy_no_match(self) -> None:
        registry = {"completely_different": lambda context=None: "ok"}
        healer = Healer(
            guard=GuardConfig(heal_retries_per_layer=0, max_effort_ms=-1.0, fuzzy_threshold=0.9),
            registry=registry,
        )

        def fail() -> Any:
            raise RuntimeError("nope")

        res = healer.execute(fail, fallback_name="xyzzy")
        assert res.success is False
        assert res.fallback_name is None


# ============================================================================
# TestHealer
# ============================================================================


class TestHealer:
    def test_execute_succeeds_on_first_try(self) -> None:
        healer = Healer(guard=GuardConfig())
        res = healer.execute(lambda: 42)
        assert res.success is True
        assert res.result == 42
        assert res.attempts == 0

    def test_execute_retries_and_succeeds_on_retry(self) -> None:
        counter = {"n": 0}

        def flaky() -> int:
            counter["n"] += 1
            if counter["n"] < 3:
                raise RuntimeError("not yet")
            return 42

        healer = Healer(
            guard=GuardConfig(
                heal_retries_per_layer=5,
                initial_backoff_ms=0.0,
                max_effort_ms=-1.0,
            )
        )
        res = healer.execute(flaky)
        assert res.success is True
        assert res.result == 42
        assert res.attempts == 2

    def test_execute_exhausts_retries(self) -> None:
        healer = Healer(
            guard=GuardConfig(
                heal_retries_per_layer=2,
                initial_backoff_ms=0.0,
                max_effort_ms=-1.0,
            )
        )

        def always_fail() -> Any:
            raise ValueError("boom")

        res = healer.execute(always_fail)
        assert res.success is False
        assert res.attempts == 3  # initial failure + 2 retries
        assert isinstance(res.error, ValueError)

    def test_execute_respects_max_effort_ms(self) -> None:
        healer = Healer(
            guard=GuardConfig(
                heal_retries_per_layer=10,
                initial_backoff_ms=10_000,
                max_effort_ms=100.0,
            )
        )

        def always_fail() -> Any:
            raise ValueError("boom")

        res = healer.execute(always_fail)
        assert res.success is False
        assert res.attempts == 1

    def test_execute_with_hooks_that_abort_before_retry(self) -> None:
        hook = _AbortingHook()
        healer = Healer(
            guard=GuardConfig(
                heal_retries_per_layer=5,
                initial_backoff_ms=0.0,
                max_effort_ms=-1.0,
            ),
            hooks=[hook],
        )

        def always_fail() -> Any:
            raise ValueError("boom")

        res = healer.execute(always_fail)
        assert res.success is False
        assert res.attempts == 1

    def test_execute_with_fuzzy_fallback_finds_match(self) -> None:
        registry = {"backup_handler": lambda context=None: "fallback"}
        healer = Healer(
            guard=GuardConfig(
                heal_retries_per_layer=0,
                max_effort_ms=-1.0,
            ),
            registry=registry,
        )

        def always_fail() -> Any:
            raise RuntimeError("nope")

        res = healer.execute(always_fail, fallback_name="backup_handler")
        assert res.success is True
        assert res.fallback_name == "backup_handler"

    def test_execute_with_fuzzy_fallback_no_match(self) -> None:
        healer = Healer(
            guard=GuardConfig(heal_retries_per_layer=0, max_effort_ms=-1.0),
            registry={"unrelated": lambda context=None: "ok"},
        )

        def always_fail() -> Any:
            raise RuntimeError("nope")

        res = healer.execute(always_fail, fallback_name="nonexistent", **{})
        assert res.success is False

    def test_child_healer_reduces_guard(self) -> None:
        parent_guard = GuardConfig(heal_retries_per_layer=5, max_effort_ms=1000.0)
        healer = Healer(guard=parent_guard)
        child = healer.child_healer()
        assert child.guard.heal_retries_per_layer == 4
        assert child.guard.max_effort_ms == pytest.approx(700.0)
        assert child.guard.layer == 1


# ============================================================================
# TestHealConvenience
# ============================================================================


class TestHealConvenience:
    def test_heal_with_default_guard(self) -> None:
        res = heal(lambda: 10)
        assert res.success is True
        assert res.result == 10

    def test_heal_with_custom_guard(self) -> None:
        guard = GuardConfig(heal_retries_per_layer=1, initial_backoff_ms=0.0, max_effort_ms=-1.0)
        res = heal(lambda: 10, guard=guard)
        assert res.success is True
        assert res.result == 10

    def test_heal_passes_fallback_name_and_registry(self) -> None:
        registry = {"fallback_fn": lambda context=None: "from-fallback"}
        res = heal(
            lambda: (_ for _ in ()).throw(RuntimeError("boom")),
            guard=GuardConfig(heal_retries_per_layer=0),
            registry=registry,
            fallback_name="fallback_fn",
        )
        assert res.success is True
        assert res.fallback_name == "fallback_fn"
