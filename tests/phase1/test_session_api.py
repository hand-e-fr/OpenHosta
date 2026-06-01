"""Integration tests — full session lifecycle CRUD + orchestration."""

from next_v5.agent import AgentEngine, AgentSession, AgentStatus


class TestCreatePauseResumeDelete:
    """Full lifecycle: create → run → pause → resume → terminate → delete."""

    def test_full_lifecycle(self) -> None:
        engine = AgentEngine(model="test-model", base_url="http://localhost")

        # Create
        s = engine.create_session(title="Lifecycle", role="dev", tags=["integration"])
        assert s.status == AgentStatus.IDLE
        assert engine.session_count == 1

        # Send message → RUNNING
        result = engine.send_message(s.session_id, "start work")
        assert result == "delivered"
        assert s.status == AgentStatus.RUNNING

        # Pause
        engine.pause_session(s.session_id)
        assert s.status == AgentStatus.PAUSED

        # Resume
        engine.resume_session(s.session_id)
        assert s.status == AgentStatus.RUNNING

        # Terminate
        s.transition_to(AgentStatus.TERMINATED)
        assert s.status == AgentStatus.TERMINATED

        # List should still show it (until deleted)
        assert len(engine.list_sessions(status=AgentStatus.TERMINATED)) == 1

        # Delete with archive
        engine.delete_session(s.session_id, archive=True)
        assert engine.session_count == 0
        assert engine.archive_count == 1


class TestMultipleSessionsOrchestration:
    """Create several sessions, run some, pause others, broadcast."""

    def test_multi_session_workflow(self) -> None:
        engine = AgentEngine(model="test-model", base_url="http://localhost")

        s_a = engine.create_session(title="Agent A", role="dev")
        s_b = engine.create_session(title="Agent B", role="dev")
        s_c = engine.create_session(title="Agent C", role="dev")

        # Start A and B
        engine.send_message(s_a.session_id, "work")
        engine.send_message(s_b.session_id, "work")

        # A and B are RUNNING, C is still IDLE
        assert engine.list_sessions(status=AgentStatus.RUNNING) == [s_a, s_b]
        assert engine.list_sessions(status=AgentStatus.IDLE) == [s_c]

        # Pause B
        engine.pause_session(s_b.session_id)
        assert s_b.status == AgentStatus.PAUSED

        # Broadcast only to RUNNING
        count = engine.broadcast(
            "urgent directive", status_filter=AgentStatus.RUNNING
        )
        assert count == 1  # only A

        # Broadcast to all non-terminal: A (RUNNING), B (PAUSED→RUNNING), C (IDLE→RUNNING)
        count = engine.broadcast("all hands")
        assert count == 3  # All three are non-terminal and accept messages

    def test_health_check_workflow(self) -> None:
        engine = AgentEngine(model="test-model", base_url="http://localhost")

        s_healthy = engine.create_session(title="Good", role="dev", tokens_limit=10_000)
        s_critical = engine.create_session(title="Hot", role="dev", tokens_limit=100)
        s_saturated = engine.create_session(title="Full", role="dev", tokens_limit=100)

        s_critical.tokens_used = 80  # 80% → critical
        s_saturated.tokens_used = 95  # 95% → saturated

        assert len(engine.healthy_sessions()) == 1
        assert len(engine.critical_sessions()) == 1
        assert len(engine.saturated_sessions()) == 1


class TestEdgeCases:
    def test_double_delete_raises(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="A", role="dev")
        engine.delete_session(s.session_id)
        import pytest

        with pytest.raises(KeyError):
            engine.delete_session(s.session_id)

    def test_archive_preserves_session_data(self) -> None:
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="Archived", role="dev", tags=["v5"])
        sid = s.session_id
        engine.delete_session(sid, archive=True)
        # Session data should be preserved in archive
        assert engine.archive_count == 1

    def test_send_message_preserves_idempotent_running(self) -> None:
        """If session is already RUNNING, send_message does not fail."""
        engine = AgentEngine(model="m", base_url="u")
        s = engine.create_session(title="A", role="dev")
        engine.send_message(s.session_id, "first")
        assert s.status == AgentStatus.RUNNING
        result = engine.send_message(s.session_id, "second")
        assert result == "delivered"
        assert s.status == AgentStatus.RUNNING
