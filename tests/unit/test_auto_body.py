"""Tests for AgentEngine.auto_body() — stub that raises NotImplementedError."""

import pytest

from openhosta.agent import AgentEngine, AgentStatus


class TestAutoBodyNotImplemented:
    """auto_body() is a typed stub that raises NotImplementedError."""

    def test_raises_not_implemented(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="T", role="r")

        with pytest.raises(NotImplementedError, match="auto_body streaming"):
            next(iter(engine.auto_body(s.session_id, "prompt")))

    def test_error_message_is_informative(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="T", role="r")

        with pytest.raises(NotImplementedError) as exc_info:
            next(iter(engine.auto_body(s.session_id, "x")))
        assert "not yet implemented" in str(exc_info.value)

    def test_yields_no_chunks(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="T", role="r")

        chunks: list[str] = []
        with pytest.raises(NotImplementedError):
            for chunk in engine.auto_body(s.session_id, "prompt"):
                chunks.append(chunk)
        assert chunks == []


class TestAutoBodySignature:
    """auto_body() has the correct method signature."""

    def test_accepts_session_id_and_message(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="T", role="r")

        gen = engine.auto_body(s.session_id, "some message")
        assert hasattr(gen, "__next__") or isinstance(gen, type(iter([])))

    def test_returns_generator_type(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="T", role="r")

        result = engine.auto_body(s.session_id, "msg")
        import types

        assert isinstance(result, types.GeneratorType)

    def test_docstring_mentions_future_contract(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        assert engine.auto_body.__doc__ is not None
        doc = engine.auto_body.__doc__
        assert "Future contract" in doc or "future" in doc.lower()


class TestAutoBodyWithVariousSessions:
    """auto_body() behaviour is consistent regardless of session state."""

    def test_raises_for_idle_session(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="T", role="r")
        assert s.status == AgentStatus.IDLE

        with pytest.raises(NotImplementedError):
            next(iter(engine.auto_body(s.session_id, "x")))

    def test_raises_for_running_session(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="T", role="r")
        engine.send_message(s.session_id, "start")
        assert s.status == AgentStatus.RUNNING

        with pytest.raises(NotImplementedError):
            next(iter(engine.auto_body(s.session_id, "x")))
