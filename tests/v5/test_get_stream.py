"""Tests for AgentSession.get_stream() — streaming generator."""

import pytest

from openhosta.agent import AgentEngine, AgentSession, AgentStatus


class TestGetStreamRunning:
    """get_stream() works when session is RUNNING and has engine ref."""

    def test_yields_chunks(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="T", role="r")
        engine.send_message(s.session_id, "hello")
        assert s.status == AgentStatus.RUNNING

        chunks = list(s.get_stream("test", interval_ms=5))
        assert len(chunks) >= 1
        assert "".join(chunks) == engine.execute_step(s.session_id, "test")

    def test_reconstructs_full_response(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="T", role="r")
        engine.send_message(s.session_id, "hello")

        chunks = list(s.get_stream("abc", interval_ms=3))
        full = "".join(chunks)
        expected = engine.execute_step(s.session_id, "abc")
        assert full == expected

    def test_chunk_size_respects_interval(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="T", role="r")
        engine.send_message(s.session_id, "hello")

        chunks = list(s.get_stream("x", interval_ms=2))
        for chunk in chunks[:-1]:
            assert len(chunk) == 2
        last = chunks[-1]
        assert 1 <= len(last) <= 2

    def test_tracks_tokens(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="T", role="r")
        engine.send_message(s.session_id, "hello")
        tokens_before = s.tokens_used

        list(s.get_stream("one two three", interval_ms=100))
        assert s.tokens_used == tokens_before + 3


class TestGetStreamNotRunning:
    """get_stream() raises RuntimeError when session is not RUNNING."""

    def test_idle_raises(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="T", role="r")
        with pytest.raises(RuntimeError, match="Session must be RUNNING"):
            next(iter(s.get_stream("msg")))

    def test_paused_raises(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="T", role="r")
        engine.send_message(s.session_id, "hello")
        engine.pause_session(s.session_id)
        with pytest.raises(RuntimeError, match="Session must be RUNNING"):
            next(iter(s.get_stream("msg")))

    def test_terminated_raises(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="T", role="r")
        engine.send_message(s.session_id, "hello")
        s.transition_to(AgentStatus.TERMINATED)
        with pytest.raises(RuntimeError, match="Session must be RUNNING"):
            next(iter(s.get_stream("msg")))


class TestGetStreamNoEngine:
    """get_stream() raises RuntimeError when engine ref is missing."""

    def test_standalone_session_raises(self) -> None:
        s = AgentSession(session_id="standalone", title="T", role="r")
        s.transition_to(AgentStatus.RUNNING)
        with pytest.raises(RuntimeError, match="no engine reference"):
            next(iter(s.get_stream("msg")))


class TestGetStreamDefaultInterval:
    """get_stream() with default interval_ms=100."""

    def test_default_interval_is_100(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="T", role="r")
        engine.send_message(s.session_id, "hello")

        chunks = list(s.get_stream("hi"))
        for chunk in chunks[:-1]:
            assert len(chunk) == 100
        assert 1 <= len(chunks[-1]) <= 100


class TestGetStreamEmptyMessage:
    """get_stream() handles short / edge-case messages."""

    def test_single_char_message(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="T", role="r")
        engine.send_message(s.session_id, "hello")

        chunks = list(s.get_stream("x", interval_ms=100))
        assert len(chunks) == 1
        assert chunks[0] == engine.execute_step(s.session_id, "x")
