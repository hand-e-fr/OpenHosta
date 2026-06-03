"""Functional tests against the real local backend (no mocks)."""

import re

import pytest

from openhosta import Agent, BackendModel
from openhosta.agent import CapabilityRegistration, infer, tool


@pytest.fixture(autouse=True)
def _clean_registry() -> None:
    reg = CapabilityRegistration()
    reg.clear()
    yield
    reg.clear()


# --------------------------------------------------------------------------- #
# Backend
# --------------------------------------------------------------------------- #

backend = BackendModel(
    provider="openai_compatible",
    model_name="cyankiwi/Qwen3.6-27B-AWQ-INT4",
    base_url="http://127.0.0.1:8000/v1",
    api_key="none",
)


# --------------------------------------------------------------------------- #
# Agent class  (renamed to avoid pytest class collection)
# --------------------------------------------------------------------------- #

@backend.compile()
class FunctionalTestAgent(Agent):
    """Agent subclass compiled against the local Qwen backend."""
    pass


# --------------------------------------------------------------------------- #
# Tests — capabilities registered inside each test to survive fixture clear
# --------------------------------------------------------------------------- #


class TestAgentFunctional:
    """End-to-end lifecycle and dispatch with the *real* backend."""

    def test_recruit(self) -> None:
        agent = FunctionalTestAgent()
        assert agent.status == "CONFIGURED"

        agent.recruit(quota=4096)

        assert agent.status == "RECRUITED"
        assert agent.agent_session is not None
        assert agent.agent_session.tokens_limit == 4096

        agent.free()

    def test_get_dispatches_tool_add(self) -> None:
        @tool(name="functional.f_add", description="Add two integers from a message")
        def add_tool(msg: str = "", **_kwargs) -> str:
            numbers = re.findall(r"\d+", msg)
            if len(numbers) >= 2:
                return str(int(numbers[0]) + int(numbers[1]))
            return "0"

        agent = FunctionalTestAgent()
        agent.recruit(quota=4096)

        result = agent.get("Add 12 and 15")

        assert "27" in str(result)

        agent.free()

    def test_free_transitions(self) -> None:
        agent = FunctionalTestAgent()
        agent.recruit()

        report = agent.free()

        assert agent.status == "FREED"
        assert report == ""

    def test_get_dispatches_infer(self) -> None:
        """When only an infer is registered, it must be dispatched."""
        @infer(name="functional.f_summarize", description="Summarize a text")
        def summarize_infer(msg: str = "", **_kwargs) -> str:
            return f"summary: {msg}"

        agent = FunctionalTestAgent()
        agent.recruit()

        result = agent.get("Summarize this text please")

        assert "summary" in str(result).lower()

        agent.free()

    def test_get_without_matching_tool_falls_back(self) -> None:
        """When no tool returns truthy for a random message, engine fallback."""
        agent = FunctionalTestAgent()
        agent.recruit()

        result = agent.get("random message with no numbers")

        assert isinstance(result, str)
        assert len(result) > 0

        agent.free()
