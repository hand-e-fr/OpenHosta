"""Tests for Agent.get() dispatch integration — Phase 3."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from openhosta.agent import (
    CapabilityDispatcher,
    CapabilityRegistration,
    CapabilityType,
    infer,
    planner,
    playbook,
    router,
    tool,
)


@pytest.fixture(autouse=True)
def _clean_registry() -> None:
    reg = CapabilityRegistration()
    reg.clear()
    yield
    reg.clear()


class TestAgentGetNotRecruited:
    def test_get_raises_runtime_error_when_configured(self) -> None:
        from openhosta.agent.agent import Agent

        agent = Agent()
        assert agent.status == "CONFIGURED"
        with pytest.raises(RuntimeError, match="Agent must be recruited first"):
            agent.get("hello")


class TestAgentGetWithDispatcher:
    def test_get_dispatches_router_first(self) -> None:
        from openhosta.agent.agent import Agent

        @router(name="dispatch.test_router", description="test router")
        def my_router(msg: str) -> str:
            return f"routed:{msg}"

        agent = Agent()

        with patch.object(agent, "_ensure_engine") as mock_ensure:
            mock_engine = MagicMock()
            mock_session = MagicMock(session_id="sess-1")
            mock_engine.create_session.return_value = mock_session
            mock_ensure.return_value = mock_engine

            agent.recruit()
            result = agent.get("test-msg")

        assert result == "routed:test-msg"

    def test_get_dispatches_planner_when_no_router(self) -> None:
        from openhosta.agent.agent import Agent

        @planner(name="dispatch.test_planner", description="test planner")
        def my_planner(msg: str) -> str:
            return f"planned:{msg}"

        agent = Agent()

        with patch.object(agent, "_ensure_engine") as mock_ensure:
            mock_engine = MagicMock()
            mock_session = MagicMock(session_id="sess-1")
            mock_engine.create_session.return_value = mock_session
            mock_ensure.return_value = mock_engine

            agent.recruit()
            result = agent.get("test-msg")

        assert result == "planned:test-msg"

    def test_get_dispatches_playbook_when_no_router_or_planner(self) -> None:
        from openhosta.agent.agent import Agent

        @playbook(name="dispatch.test_playbook", description="test playbook")
        def my_playbook(msg: str) -> str:
            return f"playbook:{msg}"

        agent = Agent()

        with patch.object(agent, "_ensure_engine") as mock_ensure:
            mock_engine = MagicMock()
            mock_session = MagicMock(session_id="sess-1")
            mock_engine.create_session.return_value = mock_session
            mock_ensure.return_value = mock_engine

            agent.recruit()
            result = agent.get("test-msg")

        assert result == "playbook:test-msg"

    def test_get_dispatches_infer_when_no_higher_priority(self) -> None:
        from openhosta.agent.agent import Agent

        @infer(name="dispatch.test_infer", description="test infer")
        def my_infer(msg: str) -> str:
            return f"inferred:{msg}"

        agent = Agent()

        with patch.object(agent, "_ensure_engine") as mock_ensure:
            mock_engine = MagicMock()
            mock_session = MagicMock(session_id="sess-1")
            mock_engine.create_session.return_value = mock_session
            mock_ensure.return_value = mock_engine

            agent.recruit()
            result = agent.get("test-msg")

        assert result == "inferred:test-msg"

    def test_get_dispatches_tool_as_last_capability(self) -> None:
        from openhosta.agent.agent import Agent

        @tool(name="dispatch.test_tool", description="test tool")
        def my_tool(msg: str) -> str:
            return f"tooled:{msg}"

        agent = Agent()

        with patch.object(agent, "_ensure_engine") as mock_ensure:
            mock_engine = MagicMock()
            mock_session = MagicMock(session_id="sess-1")
            mock_engine.create_session.return_value = mock_session
            mock_ensure.return_value = mock_engine

            agent.recruit()
            result = agent.get("test-msg")

        assert result == "tooled:test-msg"


class TestAgentGetDispatchPriority:
    def test_router_wins_over_planner(self) -> None:
        """When both router and planner are registered, router should win."""
        from openhosta.agent.agent import Agent

        @router(name="dispatch.prio_router", description="priority router")
        def my_router(msg: str) -> str:
            return "from_router"

        @planner(name="dispatch.prio_planner", description="priority planner")
        def my_planner(msg: str) -> str:
            return "from_planner"

        agent = Agent()

        with patch.object(agent, "_ensure_engine") as mock_ensure:
            mock_engine = MagicMock()
            mock_session = MagicMock(session_id="sess-1")
            mock_engine.create_session.return_value = mock_session
            mock_ensure.return_value = mock_engine

            agent.recruit()
            result = agent.get("test-msg")

        assert result == "from_router"

    def test_planner_wins_over_playbook(self) -> None:
        """When both planner and playbook are registered, planner should win."""
        from openhosta.agent.agent import Agent

        @planner(name="dispatch.prio_planner2", description="priority planner")
        def my_planner(msg: str) -> str:
            return "from_planner"

        @playbook(name="dispatch.prio_playbook", description="priority playbook")
        def my_playbook(msg: str) -> str:
            return "from_playbook"

        agent = Agent()

        with patch.object(agent, "_ensure_engine") as mock_ensure:
            mock_engine = MagicMock()
            mock_session = MagicMock(session_id="sess-1")
            mock_engine.create_session.return_value = mock_session
            mock_ensure.return_value = mock_engine

            agent.recruit()
            result = agent.get("test-msg")

        assert result == "from_planner"


class TestAgentGetFallback:
    def test_fallback_to_execute_step_when_no_capabilities(self) -> None:
        """When no capabilities are registered, fallback to engine.execute_step."""
        from openhosta.agent.agent import Agent

        agent = Agent()

        with patch.object(agent, "_ensure_engine") as mock_ensure:
            mock_engine = MagicMock()
            mock_engine.execute_step.return_value = "response to: hello"
            mock_session = MagicMock(session_id="sess-1")
            mock_engine.create_session.return_value = mock_session
            mock_ensure.return_value = mock_engine

            agent.recruit()
            result = agent.get("hello")

        assert result == "response to: hello"
        mock_engine.execute_step.assert_called_once_with("sess-1", "hello")

    def test_fallback_string_when_no_session(self) -> None:
        """When session is None, return generic fallback string."""
        from openhosta.agent.agent import Agent

        agent = Agent()
        agent.status = "RECRUITED"
        agent._agent_session = None

        with patch.object(agent, "_ensure_engine") as mock_ensure:
            mock_engine = MagicMock()
            mock_ensure.return_value = mock_engine

            result = agent.get("hello")

        assert result == "response to: hello"


class TestPlaybookPlannerRegistration:
    def test_playbook_registers_as_playbook_type(self) -> None:
        @playbook(name="dispatch.reg_pb", description="registration test")
        def example_playbook(msg: str) -> str:
            return msg

        reg = CapabilityRegistration()
        assert reg.count == 1
        _, meta = reg.get("dispatch.reg_pb")
        assert meta.capacity_type == CapabilityType.PLAYBOOK
        assert meta.description == "registration test"

    def test_planner_registers_as_planner_type(self) -> None:
        @planner(name="dispatch.reg_pl", description="registration test")
        def example_planner(msg: str) -> str:
            return msg

        reg = CapabilityRegistration()
        assert reg.count == 1
        _, meta = reg.get("dispatch.reg_pl")
        assert meta.capacity_type == CapabilityType.PLANNER
        assert meta.description == "registration test"

    def test_playbook_attaches_metadata_attribute(self) -> None:
        @playbook(name="dispatch.meta_pb", description="metadata test")
        def example_playbook() -> str:
            return "ok"

        assert hasattr(example_playbook, "_capability")
        assert example_playbook._capability.name == "dispatch.meta_pb"
        assert example_playbook._capability.capacity_type == CapabilityType.PLAYBOOK

    def test_planner_attaches_metadata_attribute(self) -> None:
        @planner(name="dispatch.meta_pl", description="metadata test")
        def example_planner() -> str:
            return "ok"

        assert hasattr(example_planner, "_capability")
        assert example_planner._capability.name == "dispatch.meta_pl"
        assert example_planner._capability.capacity_type == CapabilityType.PLANNER


class TestDispatcherIntegration:
    def test_dispatcher_find_by_type_playbook(self) -> None:
        @playbook(name="dispatch.find_pb", description="find test")
        def example_pb(msg: str) -> str:
            return msg

        dispatcher = CapabilityDispatcher()
        results = dispatcher.route_by_type(CapabilityType.PLAYBOOK, msg="test")
        assert len(results) == 1
        assert results[0].success
        assert results[0].result == "test"

    def test_dispatcher_find_by_type_planner(self) -> None:
        @planner(name="dispatch.find_pl", description="find test")
        def example_pl(msg: str) -> str:
            return msg

        dispatcher = CapabilityDispatcher()
        results = dispatcher.route_by_type(CapabilityType.PLANNER, msg="test")
        assert len(results) == 1
        assert results[0].success
        assert results[0].result == "test"
