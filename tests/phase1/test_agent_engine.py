"""Tests for AgentEngine — CRUD, metrics, orchestration."""

import pytest

from next_v5.agent import AgentEngine, AgentSession, AgentStatus


class TestEngineCreation:
    def test_default_state(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        assert engine.model == "gpt-4"
        assert engine.base_url == "http://localhost:8000"
        assert engine.session_count == 0
        assert engine.archive_count == 0


class TestCreateSession:
    def test_create_basic(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        session = engine.create_session(title="Test", role="dev")
        assert session.title == "Test"
        assert session.role == "dev"
        assert session.model == "gpt-4"
        assert engine.session_count == 1

    def test_create_with_tags(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        session = engine.create_session(
            title="Tagged", role="dev", tags=["urgent", "v5"], timeout=1200
        )
        assert session.tags == ["urgent", "v5"]
        assert session.timeout_seconds == 1200

    def test_create_multiple_sessions(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        s1 = engine.create_session(title="A", role="dev")
        s2 = engine.create_session(title="B", role="dev")
        assert engine.session_count == 2
        assert s1.session_id != s2.session_id

    def test_create_with_custom_tokens_limit(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        session = engine.create_session(title="A", role="dev", tokens_limit=512_000)
        assert session.tokens_limit == 512_000

    def test_create_returns_idled_session(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        session = engine.create_session(title="A", role="dev")
        assert session.status == AgentStatus.IDLE


class TestGetSession:
    def test_get_existing(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        s = engine.create_session(title="A", role="dev")
        retrieved = engine.get_session(s.session_id)
        assert retrieved.session_id == s.session_id

    def test_get_nonexistent_raises(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        with pytest.raises(KeyError, match="not found"):
            engine.get_session("nonexistent-id")


class TestListSessions:
    def test_list_all(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        engine.create_session(title="A", role="dev")
        engine.create_session(title="B", role="dev")
        assert len(engine.list_sessions()) == 2

    def test_list_filtered_by_status(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        engine.create_session(title="A", role="dev")
        s2 = engine.create_session(title="B", role="dev")
        # IDLE sessions only
        idle_list = engine.list_sessions(status=AgentStatus.IDLE)
        assert len(idle_list) == 2

    def test_list_empty_filter(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        engine.create_session(title="A", role="dev")
        running_list = engine.list_sessions(status=AgentStatus.RUNNING)
        assert len(running_list) == 0


class TestPauseResume:
    def test_pause_session(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        s = engine.create_session(title="A", role="dev")
        engine.send_message(s.session_id, "hello")
        assert s.status == AgentStatus.RUNNING
        paused = engine.pause_session(s.session_id)
        assert paused.status == AgentStatus.PAUSED

    def test_resume_session(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        s = engine.create_session(title="A", role="dev")
        engine.send_message(s.session_id, "hello")
        engine.pause_session(s.session_id)
        resumed = engine.resume_session(s.session_id)
        assert resumed.status == AgentStatus.RUNNING

    def test_pause_nonexistent_raises(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        with pytest.raises(KeyError):
            engine.pause_session("missing")

    def test_pause_on_idle_raises(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        s = engine.create_session(title="A", role="dev")
        with pytest.raises(ValueError):
            engine.pause_session(s.session_id)  # IDLE -> PAUSED invalid


class TestDeleteSession:
    def test_delete_with_archive(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        s = engine.create_session(title="A", role="dev")
        engine.delete_session(s.session_id, archive=True)
        assert engine.session_count == 0
        assert engine.archive_count == 1

    def test_delete_without_archive(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        s = engine.create_session(title="A", role="dev")
        engine.delete_session(s.session_id, archive=False)
        assert engine.session_count == 0
        assert engine.archive_count == 0

    def test_delete_nonexistent_raises(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        with pytest.raises(KeyError):
            engine.delete_session("missing")


class TestMetricsHealthy:
    def test_healthy_returns_low_usage_sessions(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        engine.create_session(title="A", role="dev")
        healthy = engine.healthy_sessions()
        assert len(healthy) == 1

    def test_healthy_excludes_high_usage(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        s = engine.create_session(title="A", role="dev", tokens_limit=100)
        s.tokens_used = 80  # 80% > 75%
        healthy = engine.healthy_sessions()
        assert len(healthy) == 0


class TestMetricsCritical:
    def test_critical_returns_sessions_at_75_to_90_percent(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        s = engine.create_session(title="A", role="dev", tokens_limit=100)
        s.tokens_used = 80  # 80%
        critical = engine.critical_sessions()
        assert len(critical) == 1

    def test_critical_excludes_low_usage(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        s = engine.create_session(title="A", role="dev", tokens_limit=1000)
        s.tokens_used = 100  # 10%
        critical = engine.critical_sessions()
        assert len(critical) == 0


class TestMetricsSaturated:
    def test_saturated_returns_sessions_at_90_percent_plus(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        s = engine.create_session(title="A", role="dev", tokens_limit=100)
        s.tokens_used = 90  # 90%
        saturated = engine.saturated_sessions()
        assert len(saturated) == 1

    def test_saturated_excludes_below_90(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        s = engine.create_session(title="A", role="dev", tokens_limit=100)
        s.tokens_used = 89  # 89%
        saturated = engine.saturated_sessions()
        assert len(saturated) == 0


class TestSendMessage:
    def test_send_delivers_and_transitions_to_running(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        s = engine.create_session(title="A", role="dev")
        result = engine.send_message(s.session_id, "hello world")
        assert result == "delivered"
        assert s.status == AgentStatus.RUNNING

    def test_send_adds_tokens(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        s = engine.create_session(title="A", role="dev")
        engine.send_message(s.session_id, "one two three four five")
        assert s.tokens_used == 5

    def test_send_to_terminal_returns_none(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        s = engine.create_session(title="A", role="dev")
        engine.send_message(s.session_id, "hello")
        s.transition_to(AgentStatus.TERMINATED)
        result = engine.send_message(s.session_id, "again")
        assert result is None

    def test_send_to_nonexistent_raises(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        with pytest.raises(KeyError):
            engine.send_message("missing", "hello")


class TestBroadcast:
    def test_broadcast_to_all(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        engine.create_session(title="A", role="dev")
        engine.create_session(title="B", role="dev")
        count = engine.broadcast("team message")
        assert count == 2

    def test_broadcast_filtered(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        s1 = engine.create_session(title="A", role="dev")
        s2 = engine.create_session(title="B", role="dev")
        engine.send_message(s1.session_id, "hello")  # RUNNING
        # Only RUNNING
        count = engine.broadcast("running only", status_filter=AgentStatus.RUNNING)
        assert count == 1

    def test_broadcast_empty_returns_zero(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        count = engine.broadcast("nobody")
        assert count == 0


class TestUpdateConfig:
    def test_update_model(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        s = engine.create_session(title="A", role="dev")
        engine.update_config(s.session_id, model="gpt-5")
        assert s.model == "gpt-5"

    def test_update_timeout(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        s = engine.create_session(title="A", role="dev")
        engine.update_config(s.session_id, timeout_seconds=3600)
        assert s.timeout_seconds == 3600

    def test_update_title(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        s = engine.create_session(title="A", role="dev")
        engine.update_config(s.session_id, title="New Title")
        assert s.title == "New Title"

    def test_update_nonexistent_raises(self) -> None:
        engine = AgentEngine(model="gpt-4", base_url="http://localhost:8000")
        with pytest.raises(KeyError):
            engine.update_config("missing", model="gpt-5")
