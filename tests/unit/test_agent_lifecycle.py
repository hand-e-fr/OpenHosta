"""Tests for Agent lifecycle and @backend.compile() integration."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from openhosta.backend import BackendModel


class TestAgentConfigured:
    def test_initial_status_is_configured(self) -> None:
        from openhosta.agent.agent import Agent

        agent = Agent()
        assert agent.status == "CONFIGURED"

    def test_default_attributes(self) -> None:
        from openhosta.agent.agent import Agent

        agent = Agent()
        assert agent.learning is False
        assert agent.reincarn is False
        assert agent.agent_session is None
        assert agent.agent_engine is None

    def test_learning_flag(self) -> None:
        from openhosta.agent.agent import Agent

        agent = Agent(learning=True)
        assert agent.learning is True

    def test_reincarn_flag(self) -> None:
        from openhosta.agent.agent import Agent

        agent = Agent(reincarn=True)
        assert agent.reincarn is True

    def test_workspace_default_creates_workspace(self) -> None:
        from openhosta.agent.agent import Agent

        agent = Agent()
        ws = agent.workspace
        assert ws is not None
        assert ws.root == Path(".").resolve()

    def test_workspace_provided(self) -> None:
        from openhosta.agent.agent import Agent
        from openhosta.workspace import Workspace

        tmp = Path(__file__).parent.parent.parent
        ws = Workspace(tmp)
        agent = Agent(workspace=ws)
        assert agent.workspace is ws


class TestAgentRecruit:
    def test_recruit_transitions_to_recruited(self) -> None:
        from openhosta.agent.agent import Agent

        agent = Agent()

        with patch.object(agent, "_ensure_engine") as mock_ensure:
            mock_engine = MagicMock()
            mock_session = MagicMock()
            mock_engine.create_session.return_value = mock_session
            mock_ensure.return_value = mock_engine

            result = agent.recruit()

        assert agent.status == "RECRUITED"
        assert result is agent  # chaining
        assert agent.agent_session is mock_session
        mock_engine.create_session.assert_called_once()
        mock_engine.create_session.assert_called_with(
            title="Agent", role="agent"
        )

    def test_recruit_with_quota(self) -> None:
        from openhosta.agent.agent import Agent

        agent = Agent()

        with patch.object(agent, "_ensure_engine") as mock_ensure:
            mock_engine = MagicMock()
            mock_session = MagicMock()
            mock_engine.create_session.return_value = mock_session
            mock_ensure.return_value = mock_engine

            agent.recruit(quota=1000)

        assert mock_session.tokens_limit == 1000

    def test_recruit_raises_when_not_configured(self) -> None:
        from openhosta.agent.agent import Agent

        agent = Agent()
        agent.status = "RECRUITED"

        with patch.object(agent, "_ensure_engine"):
            with pytest.raises(RuntimeError, match="Cannot recruit"):
                agent.recruit()


class TestAgentFree:
    def test_free_transitions_to_freed(self) -> None:
        from openhosta.agent.agent import Agent

        agent = Agent()
        agent.status = "RECRUITED"
        agent._agent_session = MagicMock()

        result = agent.free()

        assert agent.status == "FREED"
        assert result == ""

    def test_free_calls_transition_to_terminated(self) -> None:
        from openhosta.agent.agent import Agent
        from openhosta.agent.status import AgentStatus

        agent = Agent()
        agent.status = "RECRUITED"
        mock_session = MagicMock()
        agent._agent_session = mock_session

        agent.free()

        mock_session.transition_to.assert_called_once_with(AgentStatus.TERMINATED)

    def test_free_raises_when_not_recruited(self) -> None:
        from openhosta.agent.agent import Agent

        agent = Agent()
        with pytest.raises(RuntimeError, match="Cannot free"):
            agent.free()


class TestAgentKill:
    def test_kill_transitions_to_killed(self) -> None:
        from openhosta.agent.agent import Agent

        agent = Agent()
        agent.status = "RECRUITED"
        agent._agent_session = MagicMock()

        agent.kill()

        assert agent.status == "KILLED"

    def test_kill_calls_transition_to_failed(self) -> None:
        from openhosta.agent.agent import Agent
        from openhosta.agent.status import AgentStatus

        agent = Agent()
        agent.status = "RECRUITED"
        mock_session = MagicMock()
        agent._agent_session = mock_session

        agent.kill()

        mock_session.transition_to.assert_called_once_with(AgentStatus.FAILED)

    def test_kill_without_session(self) -> None:
        from openhosta.agent.agent import Agent

        agent = Agent()
        agent._agent_session = None

        agent.kill()

        assert agent.status == "KILLED"


class TestAgentGet:
    def test_get_not_implemented(self) -> None:
        from openhosta.agent.agent import Agent

        agent = Agent()
        with pytest.raises(NotImplementedError, match="Phase 3"):
            agent.get("hello")


class TestBackendCompileIntegration:
    def test_backend_model_compile_assigns_attribute(self) -> None:
        bm = BackendModel(
            provider="test", model_name="m", base_url="http://x"
        )

        @bm.compile()
        class MyAgent:
            pass

        assert hasattr(MyAgent, "_backend")
        assert MyAgent._backend is bm

    def test_agent_uses_class_backend(self) -> None:
        from openhosta.agent.agent import Agent

        bm = BackendModel(
            provider="test", model_name="m", base_url="http://x"
        )

        @bm.compile()
        class MyAgent(Agent):
            pass

        agent = MyAgent()
        assert agent._backend is bm

    def test_agent_init_backend_overrides_class(self) -> None:
        from openhosta.agent.agent import Agent

        bm1 = BackendModel(
            provider="a", model_name="m1", base_url="http://a"
        )
        bm2 = BackendModel(
            provider="b", model_name="m2", base_url="http://b"
        )

        @bm1.compile()
        class MyAgent(Agent):
            pass

        agent = MyAgent(backend=bm2)
        assert agent._backend is bm2

    def test_agent_default_backend_none(self) -> None:
        from openhosta.agent.agent import Agent

        agent = Agent()
        assert agent._backend is None


class TestAgentSubclass:
    def test_agent_is_inheritable(self) -> None:
        from openhosta.agent.agent import Agent

        class MyAgent(Agent):
            pass

        agent = MyAgent()
        assert isinstance(agent, Agent)
        assert agent.status == "CONFIGURED"

    def test_notes_independent_per_instance(self) -> None:
        from openhosta.agent.agent import Agent

        a1 = Agent()
        a2 = Agent()
        a1.notes.append("a1 note")
        assert a1.notes == ["a1 note"]
        assert a2.notes == []


class TestEnsureEngine:
    def test_ensure_engine_with_backend_model(self) -> None:
        from openhosta.agent.agent import Agent

        bm = BackendModel(
            provider="test", model_name="gpt-4", base_url="http://x"
        )
        agent = Agent(backend=bm)
        engine = agent._ensure_engine()

        assert engine.model == "gpt-4"
        assert engine.base_url == "http://x"

    def test_ensure_engine_with_backend_selector(self) -> None:
        from openhosta.agent.agent import Agent
        from openhosta.backend import BackendSelector

        bm = BackendModel(
            provider="test", model_name="llama", base_url="http://y"
        )
        selector = BackendSelector([bm])
        agent = Agent(backend=selector)
        engine = agent._ensure_engine()

        assert engine.model == "llama"
        assert engine.base_url == "http://y"
