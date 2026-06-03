"""Tests for traces module — GuardMetadata, InteractionTrace, WorkspaceActivity, ExecutionTrace.

DEF-TRACE-001 — Immutable-append trace classes with guard metadata
"""

from __future__ import annotations

import time

import pytest

from openhosta.agent import (
    ActivityKind,
    ExecutionTrace,
    GuardMetadata,
    InteractionTrace,
    TurnRole,
    WorkspaceActivity,
)

# ============================================================================
# TestGuardMetadata
# ============================================================================


class TestGuardMetadata:
    def test_defaults(self) -> None:
        g = GuardMetadata(scope="default")
        assert g.scope == "default"
        assert g.allowed_tools == ()
        assert g.denied_tools == ()
        assert g.max_tokens == -1
        assert g.max_steps == -1
        assert g.required_confirmations == ()
        assert g.description == ""

    def test_tool_allowed_no_restrictions(self) -> None:
        g = GuardMetadata(scope="open")
        assert g.tool_allowed("any_tool") is True

    def test_tool_allowed_whitelist_passes(self) -> None:
        g = GuardMetadata(scope="restricted", allowed_tools=("read", "write"))
        assert g.tool_allowed("read") is True
        assert g.tool_allowed("write") is True
        assert g.tool_allowed("execute") is False

    def test_denied_tools_checked_first(self) -> None:
        g = GuardMetadata(
            scope="deny-first",
            allowed_tools=("read", "write", "execute"),
            denied_tools=("execute",),
        )
        assert g.tool_allowed("execute") is False
        assert g.tool_allowed("read") is True

    def test_requires_confirmation(self) -> None:
        g = GuardMetadata(
            scope="confirmable",
            required_confirmations=("delete", "rm"),
        )
        assert g.requires_confirmation("delete") is True
        assert g.requires_confirmation("read") is False

    def test_has_limits(self) -> None:
        g1 = GuardMetadata(scope="a", max_tokens=1000, max_steps=10)
        assert g1.has_token_limit is True
        assert g1.has_step_limit is True

        g2 = GuardMetadata(scope="b")
        assert g2.has_token_limit is False
        assert g2.has_step_limit is False

    def test_frozen(self) -> None:
        g = GuardMetadata(scope="x")
        with pytest.raises(AttributeError):  # FrozenInstanceError
            g.scope = "y"  # type: ignore[assignment]


# ============================================================================
# TestInteractionTrace
# ============================================================================


class TestInteractionTrace:
    def test_empty_trace(self) -> None:
        t = InteractionTrace(trace_id="t1")
        assert t.is_empty is True
        assert t.turn_count == 0
        assert t.turns == ()

    def test_append_human(self) -> None:
        t = InteractionTrace(trace_id="t1")
        t2 = t.append_human("Hello")
        assert t.is_empty is True  # original unchanged
        assert t2.turn_count == 1
        assert t2.turns[0].role == TurnRole.HUMAN
        assert t2.turns[0].content == "Hello"

    def test_append_agent(self) -> None:
        t = InteractionTrace(trace_id="t1")
        t2 = t.append_agent("Hi there")
        assert t2.turns[0].role == TurnRole.AGENT
        assert t2.turns[0].content == "Hi there"

    def test_append_system(self) -> None:
        t = InteractionTrace(trace_id="t1")
        t2 = t.append_system("System message")
        assert t2.turns[0].role == TurnRole.SYSTEM
        assert t2.turns[0].content == "System message"

    def test_append_preserves_old_turns(self) -> None:
        t = InteractionTrace(trace_id="t1")
        t = t.append_human("Q")
        t = t.append_agent("A")
        assert t.turn_count == 2
        assert t.turns[0].role == TurnRole.HUMAN
        assert t.turns[1].role == TurnRole.AGENT

    def test_append_with_metadata(self) -> None:
        t = InteractionTrace(trace_id="t1")
        t2 = t.append_agent("Response", metadata={"tool_call": "file.read"})
        assert t2.turns[0].metadata["tool_call"] == "file.read"

    def test_multiple_appends_chain(self) -> None:
        t = InteractionTrace(trace_id="t1")
        t = t.append_human("1")
        t = t.append_agent("2")
        t = t.append_system("3")
        t = t.append_human("4")
        assert t.turn_count == 4

    def test_trace_id_preserved(self) -> None:
        t = InteractionTrace(trace_id="abc")
        t2 = t.append_human("x")
        assert t2.trace_id == "abc"

    def test_frozen(self) -> None:
        t = InteractionTrace(trace_id="t1")
        t2 = t.append_human("x")
        # Original t should be truly frozen
        with pytest.raises(AttributeError):
            t2.turns = ()  # type: ignore[assignment]


# ============================================================================
# TestWorkspaceActivity
# ============================================================================


class TestWorkspaceActivity:
    def test_empty(self) -> None:
        w = WorkspaceActivity(activity_id="w1")
        assert w.is_empty is True
        assert w.record_count == 0

    def test_append_record(self) -> None:
        w = WorkspaceActivity(activity_id="w1")
        w2 = w.append_record(ActivityKind.FILE_READ, "/foo/bar.txt")
        assert w.is_empty is True  # original unchanged
        assert w2.record_count == 1
        assert w2.records[0].kind == ActivityKind.FILE_READ
        assert w2.records[0].path == "/foo/bar.txt"

    def test_append_multiple(self) -> None:
        w = WorkspaceActivity(activity_id="w1")
        w = w.append_record(ActivityKind.FILE_READ, "/a.txt")
        w = w.append_record(ActivityKind.FILE_WRITE, "/b.txt")
        assert w.record_count == 2

    def test_append_with_details(self) -> None:
        w = WorkspaceActivity(activity_id="w1")
        w2 = w.append_record(
            ActivityKind.FILE_WRITE, "/out.txt", details={"bytes": 1024}
        )
        assert w2.records[0].details["bytes"] == 1024

    def test_filter_by_kind(self) -> None:
        w = WorkspaceActivity(activity_id="w1")
        w = w.append_record(ActivityKind.FILE_READ, "/a.txt")
        w = w.append_record(ActivityKind.FILE_WRITE, "/b.txt")
        w = w.append_record(ActivityKind.FILE_READ, "/c.txt")
        filtered = w.filter_by_kind(ActivityKind.FILE_READ)
        assert filtered.record_count == 2
        assert all(r.kind == ActivityKind.FILE_READ for r in filtered.records)

    def test_filter_by_path_prefix(self) -> None:
        w = WorkspaceActivity(activity_id="w1")
        w = w.append_record(ActivityKind.FILE_READ, "/src/a.py")
        w = w.append_record(ActivityKind.FILE_READ, "/src/b.py")
        w = w.append_record(ActivityKind.FILE_READ, "/other/c.py")
        filtered = w.filter_by_path_prefix("/src/")
        assert filtered.record_count == 2

    def test_activity_id_preserved(self) -> None:
        w = WorkspaceActivity(activity_id="w42")
        w2 = w.append_record(ActivityKind.FILE_READ, "/x")
        assert w2.activity_id == "w42"
        filtered = w2.filter_by_kind(ActivityKind.FILE_READ)
        assert filtered.activity_id == "w42"

    def test_timestamp_auto(self) -> None:
        before = time.time()
        w = WorkspaceActivity(activity_id="w1")
        w2 = w.append_record(ActivityKind.FILE_READ, "/x")
        after = time.time()
        assert before <= w2.records[0].timestamp <= after

    def test_frozen(self) -> None:
        w = WorkspaceActivity(activity_id="w1")
        w2 = w.append_record(ActivityKind.FILE_READ, "/x")
        with pytest.raises(AttributeError):
            w2.records = ()  # type: ignore[assignment]


# ============================================================================
# TestExecutionTrace
# ============================================================================


class TestExecutionTrace:
    def _make(self, **kwargs) -> ExecutionTrace:
        defaults: dict = {
            "execution_id": "e1",
            "session_id": "s1",
            "interaction_trace": InteractionTrace(trace_id="it1"),
            "workspace_activity": WorkspaceActivity(activity_id="wa1"),
        }
        defaults.update(kwargs)
        return ExecutionTrace(**defaults)

    def test_defaults(self) -> None:
        e = self._make()
        assert e.outcome == "running"
        assert e.ended_at is None
        assert e.error is None
        assert e.is_finished is False
        assert e.is_success is False

    def test_finish_success(self) -> None:
        e = self._make()
        e2 = e.finish("success")
        assert e.is_finished is False  # original unfinished
        assert e2.is_finished is True
        assert e2.outcome == "success"
        assert e2.is_success is True
        assert e2.error is None

    def test_finish_error(self) -> None:
        e = self._make()
        e2 = e.finish("error", error="something broke")
        assert e2.is_finished is True
        assert e2.outcome == "error"
        assert e2.error == "something broke"
        assert e2.is_success is False

    def test_duration_running(self) -> None:
        e = self._make()
        time.sleep(0.05)
        assert e.duration >= 0.05

    def test_duration_finished(self) -> None:
        e = self._make()
        time.sleep(0.05)
        e2 = e.finish("success")
        assert e2.duration >= 0.05

    def test_with_interaction(self) -> None:
        it = InteractionTrace(trace_id="it2").append_human("hello")
        e = self._make()
        e2 = e.with_interaction(it)
        assert e2.interaction_trace is it
        assert e2.turn_count == 1

    def test_with_workspace(self) -> None:
        wa = WorkspaceActivity(activity_id="wa2").append_record(
            ActivityKind.FILE_READ, "/x"
        )
        e = self._make()
        e2 = e.with_workspace(wa)
        assert e2.workspace_activity is wa
        assert e2.activity_count == 1

    def test_guard_metadata_optional(self) -> None:
        e = self._make()
        assert e.guard_metadata is None

        guard = GuardMetadata(scope="test")
        e2 = self._make(guard_metadata=guard)
        assert e2.guard_metadata is guard

    def test_frozen(self) -> None:
        e = self._make()
        e2 = e.finish("success")
        with pytest.raises(AttributeError):
            e2.outcome = "running"  # type: ignore[assignment]
