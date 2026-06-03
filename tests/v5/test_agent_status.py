"""Tests for AgentStatus enum — lifecycle state machine."""

import pytest

from openhosta.agent import AgentStatus


class TestAgentStatusValues:
    """Verify every enum member exists and is distinct."""

    def test_idle_exists(self) -> None:
        assert AgentStatus.IDLE is not None

    def test_running_exists(self) -> None:
        assert AgentStatus.RUNNING is not None

    def test_paused_exists(self) -> None:
        assert AgentStatus.PAUSED is not None

    def test_waiting_exists(self) -> None:
        assert AgentStatus.WAITING is not None

    def test_terminated_exists(self) -> None:
        assert AgentStatus.TERMINATED is not None

    def test_failed_exists(self) -> None:
        assert AgentStatus.FAILED is not None

    def test_timed_out_exists(self) -> None:
        assert AgentStatus.TIMED_OUT is not None

    def test_all_distinct(self) -> None:
        members = list(AgentStatus)
        assert len(members) == 7
        assert len(set(members)) == 7


class TestValidTransitions:
    """Verify the allowed transition matrix."""

    def test_valid_transitions_is_dict(self) -> None:
        result = AgentStatus.valid_transitions()
        assert isinstance(result, dict)

    def test_all_statuses_in_map(self) -> None:
        mapping = AgentStatus.valid_transitions()
        for status in AgentStatus:
            assert status in mapping

    def test_idle_to_running_allowed(self) -> None:
        assert AgentStatus.IDLE.can_transition_to(AgentStatus.RUNNING)

    def test_idle_to_paused_not_allowed(self) -> None:
        assert not AgentStatus.IDLE.can_transition_to(AgentStatus.PAUSED)

    def test_running_to_pause_allowed(self) -> None:
        assert AgentStatus.RUNNING.can_transition_to(AgentStatus.PAUSED)

    def test_running_to_idle_allowed(self) -> None:
        assert AgentStatus.RUNNING.can_transition_to(AgentStatus.IDLE)

    def test_running_to_waiting_allowed(self) -> None:
        assert AgentStatus.RUNNING.can_transition_to(AgentStatus.WAITING)

    def test_running_to_terminated_allowed(self) -> None:
        assert AgentStatus.RUNNING.can_transition_to(AgentStatus.TERMINATED)

    def test_running_to_failed_allowed(self) -> None:
        assert AgentStatus.RUNNING.can_transition_to(AgentStatus.FAILED)

    def test_running_to_timed_out_allowed(self) -> None:
        assert AgentStatus.RUNNING.can_transition_to(AgentStatus.TIMED_OUT)

    def test_paused_to_running_allowed(self) -> None:
        assert AgentStatus.PAUSED.can_transition_to(AgentStatus.RUNNING)

    def test_paused_to_terminated_allowed(self) -> None:
        assert AgentStatus.PAUSED.can_transition_to(AgentStatus.TERMINATED)

    def test_paused_to_idle_not_allowed(self) -> None:
        assert not AgentStatus.PAUSED.can_transition_to(AgentStatus.IDLE)

    def test_waiting_to_running_allowed(self) -> None:
        assert AgentStatus.WAITING.can_transition_to(AgentStatus.RUNNING)

    def test_waiting_to_failed_allowed(self) -> None:
        assert AgentStatus.WAITING.can_transition_to(AgentStatus.FAILED)

    def test_terminated_no_transitions(self) -> None:
        assert not AgentStatus.TERMINATED.can_transition_to(AgentStatus.IDLE)
        allowed = AgentStatus.valid_transitions()[AgentStatus.TERMINATED]
        assert allowed == []

    def test_failed_no_transitions(self) -> None:
        assert not AgentStatus.FAILED.can_transition_to(AgentStatus.IDLE)
        allowed = AgentStatus.valid_transitions()[AgentStatus.FAILED]
        assert allowed == []

    def test_timed_out_no_transitions(self) -> None:
        assert not AgentStatus.TIMED_OUT.can_transition_to(AgentStatus.IDLE)
        allowed = AgentStatus.valid_transitions()[AgentStatus.TIMED_OUT]
        assert allowed == []


class TestIsTerminal:
    def test_terminated_is_terminal(self) -> None:
        assert AgentStatus.TERMINATED.is_terminal

    def test_failed_is_terminal(self) -> None:
        assert AgentStatus.FAILED.is_terminal

    def test_timed_out_is_terminal(self) -> None:
        assert AgentStatus.TIMED_OUT.is_terminal

    def test_idle_not_terminal(self) -> None:
        assert not AgentStatus.IDLE.is_terminal

    def test_running_not_terminal(self) -> None:
        assert not AgentStatus.RUNNING.is_terminal


class TestIsActive:
    def test_idle_is_active(self) -> None:
        assert AgentStatus.IDLE.is_active

    def test_running_is_active(self) -> None:
        assert AgentStatus.RUNNING.is_active

    def test_paused_is_active(self) -> None:
        assert AgentStatus.PAUSED.is_active

    def test_terminated_not_active(self) -> None:
        assert not AgentStatus.TERMINATED.is_active

    def test_failed_not_active(self) -> None:
        assert not AgentStatus.FAILED.is_active


class TestIsSuspended:
    def test_paused_is_suspended(self) -> None:
        assert AgentStatus.PAUSED.is_suspended

    def test_waiting_is_suspended(self) -> None:
        assert AgentStatus.WAITING.is_suspended

    def test_idle_not_suspended(self) -> None:
        assert not AgentStatus.IDLE.is_suspended

    def test_running_not_suspended(self) -> None:
        assert not AgentStatus.RUNNING.is_suspended
