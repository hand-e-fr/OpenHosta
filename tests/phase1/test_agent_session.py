"""Tests for AgentSession — creation, transitions, metrics."""

import time

import pytest

from next_v5.agent import AgentSession, AgentStatus


class TestAgentSessionCreation:
    def test_default_values(self) -> None:
        s = AgentSession(session_id="s1", title="test", role="r")
        assert s.session_id == "s1"
        assert s.title == "test"
        assert s.role == "r"
        assert s.status == AgentStatus.IDLE
        assert s.tokens_used == 0
        assert s.tokens_limit == 256_000
        assert s.age_seconds == 0.0
        assert s.model == ""
        assert s.timeout_seconds == 600.0
        assert s.tags == []

    def test_custom_values(self) -> None:
        s = AgentSession(
            session_id="s2",
            title="custom",
            role="admin",
            tokens_limit=500_000,
            model="gpt-4",
            timeout_seconds=1200.0,
            tags=["urgent"],
        )
        assert s.tokens_limit == 500_000
        assert s.model == "gpt-4"
        assert s.timeout_seconds == 1200.0
        assert s.tags == ["urgent"]


class TestAgentSessionTransitions:
    def test_idle_to_running(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        s.transition_to(AgentStatus.RUNNING)
        assert s.status == AgentStatus.RUNNING

    def test_running_to_idle(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        s.transition_to(AgentStatus.RUNNING)
        s.transition_to(AgentStatus.IDLE)
        assert s.status == AgentStatus.IDLE

    def test_running_to_paused(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        s.transition_to(AgentStatus.RUNNING)
        s.transition_to(AgentStatus.PAUSED)
        assert s.status == AgentStatus.PAUSED

    def test_paused_to_running(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        s.transition_to(AgentStatus.RUNNING)
        s.transition_to(AgentStatus.PAUSED)
        s.transition_to(AgentStatus.RUNNING)
        assert s.status == AgentStatus.RUNNING

    def test_running_to_waiting(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        s.transition_to(AgentStatus.RUNNING)
        s.transition_to(AgentStatus.WAITING)
        assert s.status == AgentStatus.WAITING

    def test_waiting_to_running(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        s.transition_to(AgentStatus.RUNNING)
        s.transition_to(AgentStatus.WAITING)
        s.transition_to(AgentStatus.RUNNING)
        assert s.status == AgentStatus.RUNNING

    def test_running_to_terminated(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        s.transition_to(AgentStatus.RUNNING)
        s.transition_to(AgentStatus.TERMINATED)
        assert s.status == AgentStatus.TERMINATED

    def test_running_to_failed(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        s.transition_to(AgentStatus.RUNNING)
        s.transition_to(AgentStatus.FAILED)
        assert s.status == AgentStatus.FAILED

    def test_running_to_timed_out(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        s.transition_to(AgentStatus.RUNNING)
        s.transition_to(AgentStatus.TIMED_OUT)
        assert s.status == AgentStatus.TIMED_OUT

    def test_paused_to_terminated(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        s.transition_to(AgentStatus.RUNNING)
        s.transition_to(AgentStatus.PAUSED)
        s.transition_to(AgentStatus.TERMINATED)
        assert s.status == AgentStatus.TERMINATED

    def test_waiting_to_failed(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        s.transition_to(AgentStatus.RUNNING)
        s.transition_to(AgentStatus.WAITING)
        s.transition_to(AgentStatus.FAILED)
        assert s.status == AgentStatus.FAILED

    def test_invalid_transition_raises(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        with pytest.raises(ValueError, match="Invalid transition"):
            s.transition_to(AgentStatus.PAUSED)  # IDLE -> PAUSED invalid

    def test_terminal_cannot_transition(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        s.transition_to(AgentStatus.RUNNING)
        s.transition_to(AgentStatus.TERMINATED)
        with pytest.raises(ValueError):
            s.transition_to(AgentStatus.RUNNING)


class TestUtilizationRatio:
    def test_zero_usage(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        assert s.utilization_ratio() == 0.0

    def test_normal_usage(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r", tokens_limit=1000)
        s.tokens_used = 500
        assert s.utilization_ratio() == 0.5

    def test_full_usage(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r", tokens_limit=1000)
        s.tokens_used = 1000
        assert s.utilization_ratio() == 1.0

    def test_overflow(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r", tokens_limit=1000)
        s.tokens_used = 1500
        assert s.utilization_ratio() == 1.5

    def test_zero_limit_returns_one(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r", tokens_limit=0)
        assert s.utilization_ratio() == 1.0

    def test_negative_limit_returns_one(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r", tokens_limit=-10)
        assert s.utilization_ratio() == 1.0


class TestIsHealthy:
    def test_idle_healthy_default(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        assert s.is_healthy()

    def test_low_usage_healthy(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r", tokens_limit=1000)
        s.tokens_used = 100
        assert s.is_healthy()

    def test_high_usage_not_healthy(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r", tokens_limit=1000)
        s.tokens_used = 750
        assert not s.is_healthy()

    def test_terminal_not_healthy(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        s.transition_to(AgentStatus.RUNNING)
        s.transition_to(AgentStatus.TERMINATED)
        assert not s.is_healthy()

    def test_failed_not_healthy(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        s.transition_to(AgentStatus.RUNNING)
        s.transition_to(AgentStatus.FAILED)
        assert not s.is_healthy()

    def test_timed_out_not_healthy(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        s.transition_to(AgentStatus.RUNNING)
        s.transition_to(AgentStatus.TIMED_OUT)
        assert not s.is_healthy()

    def test_exceeds_timeout_not_healthy(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        s.timeout_seconds = 1.0
        s.age_seconds = 2.0
        assert not s.is_healthy()


class TestIsSaturatedAndIsCritical:
    def test_not_critical_at_50_percent(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r", tokens_limit=1000)
        s.tokens_used = 500
        assert not s.is_critical
        assert not s.is_saturated

    def test_critical_at_80_percent(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r", tokens_limit=1000)
        s.tokens_used = 800
        assert s.is_critical
        assert not s.is_saturated

    def test_saturated_at_95_percent(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r", tokens_limit=1000)
        s.tokens_used = 950
        assert not s.is_critical  # saturated, not critical (>= 0.90)
        assert s.is_saturated


class TestTickAge:
    def test_tick_age_increases(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        age_0 = s.tick_age()
        time.sleep(0.05)
        age_1 = s.tick_age()
        assert age_1 > age_0

    def test_tick_age_updates_last_activity(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        before = time.time()
        s.tick_age()
        assert s.last_activity >= before


class TestTransitionUpdatesLastActivity:
    def test_last_activity_changes_on_transition(self) -> None:
        s = AgentSession(session_id="s1", title="t", role="r")
        before = s.last_activity
        time.sleep(0.05)
        s.transition_to(AgentStatus.RUNNING)
        assert s.last_activity > before
