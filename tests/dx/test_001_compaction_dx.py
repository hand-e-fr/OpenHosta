"""DX test 001 — Context Compaction agent against real backend.

Exercises the DX of authoring an agent with a read_file tool and a compact
inference, using a real temporary workspace and the real local LLM backend.
"""

import tempfile
from pathlib import Path

import pytest

from openhosta import Agent, BackendModel, Workspace
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
class ContextCompactionAgent(Agent):
    """Compacts conversation history via workspace-backed reading + inference."""
    pass


# --------------------------------------------------------------------------- #
# State shared between tool and test
# --------------------------------------------------------------------------- #

_workspace: Workspace | None = None


# --------------------------------------------------------------------------- #
# Tests — capabilities registered inside each test
# --------------------------------------------------------------------------- #


class TestContextCompactionDX:
    """DX-oriented scenario: write agent -> recruit -> compact -> free."""

    def test_compaction_dxpipeline(self) -> None:
        global _workspace

        # 1. Temporary workspace
        tmp = tempfile.mkdtemp()
        _workspace = Workspace(tmp)

        # Seed a sample conversation file
        sample_file = Path(tmp) / "conversation.txt"
        sample_file.write_text(
            "User: Hello, what is OpenHosta?\n"
            "Assistant: OpenHosta is a semantic layer for Python.\n"
            "User: Can you explain guarded types?\n"
            "Assistant: Guarded types wrap Python values with validation.\n"
            "User: Thanks!\n",
            encoding="utf-8",
        )

        # Register capabilities for this test
        @tool(
            name="dx.c_compaction.read_file",
            description="Read a file from workspace",
        )
        def read_file(msg: str = "", **_kwargs) -> str:
            if _workspace is None:
                return "[workspace not set]"
            try:
                return _workspace.read(msg)
            except Exception as exc:
                return f"[read error]: {exc}"

        @infer(
            name="dx.c_compaction.compact",
            description="Compact conversation history",
        )
        def compact(msg: str = "", **_kwargs) -> str:
            lines = [line.strip() for line in msg.split("\n") if line.strip()]
            summary_words = " ".join(lines[:20])
            return f"Summary of {len(lines)} lines: {summary_words}"

        # 2. Recruit agent with real backend
        agent = ContextCompactionAgent(workspace=_workspace)
        assert agent.status == "CONFIGURED"

        agent.recruit()
        assert agent.status == "RECRUITED"

        # 3. Invoke via agent.get — dispatches to tool (read_file) or infer (compact)
        result = agent.get("Compact the conversation history")

        # 4. Assert result is non-empty and contains summary keywords
        assert len(result) > 0, "Compact result must not be empty"
        result_lower = result.lower()
        assert any(
            kw in result_lower
            for kw in ("summary", "line", "compact", "conversation")
        ), f"Result should contain summary/compaction keywords, got: {result!r}"

        # 5. Free agent
        report = agent.free()
        assert agent.status == "FREED"
        assert report == ""

    def test_compaction_with_file_read(self) -> None:
        global _workspace

        tmp = tempfile.mkdtemp()
        _workspace = Workspace(tmp)

        sample_file = Path(tmp) / "notes.md"
        sample_file.write_text(
            "# Meeting Notes\n"
            "1. Discuss project timeline\n"
            "2. Review budget allocation\n"
            "3. Assign action items\n",
            encoding="utf-8",
        )

        # Register tool for file reading
        @tool(
            name="dx.c_compaction2.read_file",
            description="Read a file from workspace",
        )
        def read_file(msg: str = "", **_kwargs) -> str:
            if _workspace is None:
                return "[workspace not set]"
            try:
                return _workspace.read(msg)
            except Exception as exc:
                return f"[read error]: {exc}"

        @infer(
            name="dx.c_compaction2.compact",
            description="Compact text",
        )
        def compact(msg: str = "", **_kwargs) -> str:
            lines = [line.strip() for line in msg.split("\n") if line.strip()]
            summary_words = " ".join(lines[:20])
            return f"Summary of {len(lines)} lines: {summary_words}"

        agent = ContextCompactionAgent(workspace=_workspace)
        agent.recruit()

        # Read the file via the tool
        read_result = agent.get("notes.md")
        assert len(read_result) > 0

        # Compact the content
        compact_result = agent.get("Compact meeting notes")
        assert len(compact_result) > 0
        compact_lower = compact_result.lower()
        assert any(
            kw in compact_lower
            for kw in ("summary", "line", "compact", "meeting", "note")
        )

        agent.free()
        assert agent.status == "FREED"
