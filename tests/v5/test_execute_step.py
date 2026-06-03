"""Tests for AgentEngine.execute_step() — single-step execution."""

import pytest

from openhosta.agent import AgentEngine


class TestExecuteStepBasic:
    """execute_step() returns simulated response and tracks tokens."""

    def test_returns_response_string(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="T", role="r")

        result = engine.execute_step(s.session_id, "hello world")
        assert isinstance(result, str)
        assert "hello world" in result

    def test_tracks_tokens(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="T", role="r")
        tokens_before = s.tokens_used

        engine.execute_step(s.session_id, "one two three")
        assert s.tokens_used == tokens_before + 3

    def test_response_contains_message(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="T", role="r")

        result = engine.execute_step(s.session_id, "test message")
        assert "test message" in result


class TestExecuteStepNonexistent:
    """execute_step() raises KeyError for unknown session."""

    def test_raises_key_error(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        with pytest.raises(KeyError, match="not found"):
            engine.execute_step("nonexistent", "msg")
