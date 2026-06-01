"""Tests for tasklist module — TaskStep, TaskList, TaskStepStatus.

DEF-TASKLIST-STATE-001 — TaskList state management with version tracking
"""

from __future__ import annotations

import time

import pytest

from next_v5.agent import TaskList, TaskStep, TaskStepStatus

# ============================================================================
# TestTaskStep
# ============================================================================


class TestTaskStep:
    def test_defaults(self) -> None:
        s = TaskStep(step_id="s1", description="do stuff")
        assert s.status == TaskStepStatus.PENDING
        assert s.priority == 0
        assert s.completed_at is None
        assert s.result is None
        assert s.error is None
        assert s.is_terminal is False
        assert s.is_active is False

    def test_terminal_states(self) -> None:
        completed = TaskStep(step_id="c", description="ok", status=TaskStepStatus.COMPLETED)
        assert completed.is_terminal is True
        assert completed.is_active is False

        failed = TaskStep(step_id="f", description="err", status=TaskStepStatus.FAILED)
        assert failed.is_terminal is True

        cancelled = TaskStep(step_id="x", description="no", status=TaskStepStatus.CANCELLED)
        assert cancelled.is_terminal is True

    def test_active_state(self) -> None:
        s = TaskStep(step_id="a", description="busy", status=TaskStepStatus.IN_PROGRESS)
        assert s.is_active is True
        assert s.is_terminal is False

    def test_pending_not_terminal(self) -> None:
        s = TaskStep(step_id="p", description="waiting")
        assert s.is_terminal is False
        assert s.is_active is False


# ============================================================================
# TestTaskListCreation
# ============================================================================


class TestTaskListCreation:
    def test_minimal(self) -> None:
        tl = TaskList(session_id="s1")
        assert tl.title == ""
        assert tl.total_steps == 0
        assert tl.version == 0
        assert tl.current_step_id is None
        assert tl.overall_progress == 0.0

    def test_custom_title(self) -> None:
        tl = TaskList(session_id="s1", title="My Plan")
        assert tl.title == "My Plan"

    def test_version_start_at_zero(self) -> None:
        tl = TaskList(session_id="s1")
        assert tl.version == 0


# ============================================================================
# TestTaskListAddStep
# ============================================================================


class TestTaskListAddStep:
    def test_add_single_step(self) -> None:
        tl = TaskList(session_id="s1")
        step = tl.add_step("step1", "Do thing")
        assert tl.total_steps == 1
        assert tl.version == 1
        assert step.step_id == "step1"
        assert step.status == TaskStepStatus.PENDING

    def test_add_multiple_steps(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("s1", "First")
        tl.add_step("s2", "Second")
        tl.add_step("s3", "Third")
        assert tl.total_steps == 3
        assert tl.version == 3

    def test_add_with_priority(self) -> None:
        tl = TaskList(session_id="s1")
        s = tl.add_step("s1", "Important", priority=-10)
        assert s.priority == -10

    def test_add_duplicate_id_raises(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("s1", "First")
        with pytest.raises(ValueError, match="already exists"):
            tl.add_step("s1", "Duplicate")

    def test_add_updates_version(self) -> None:
        tl = TaskList(session_id="s1")
        assert tl.version == 0
        tl.add_step("s1", "A")
        assert tl.version == 1
        tl.add_step("s2", "B")
        assert tl.version == 2


# ============================================================================
# TestTaskListStartCompleteFailCancel
# ============================================================================


class TestTaskListLifecycle:
    def test_start_step(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("s1", "Task")
        step = tl.start_step("s1")
        assert step.status == TaskStepStatus.IN_PROGRESS
        assert tl.current_step_id == "s1"
        assert tl.version == 2  # add + start

    def test_start_nonexistent_raises(self) -> None:
        tl = TaskList(session_id="s1")
        with pytest.raises(KeyError, match="not found"):
            tl.start_step("missing")

    def test_start_non_pending_raises(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("s1", "Task")
        tl.start_step("s1")
        with pytest.raises(ValueError, match="only PENDING"):
            tl.start_step("s1")

    def test_complete_step(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("s1", "Task")
        step = tl.complete_step("s1", result="done")
        assert step.status == TaskStepStatus.COMPLETED
        assert step.result == "done"
        assert step.completed_at is not None
        assert tl.overall_progress == 1.0

    def test_complete_terminal_raises(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("s1", "Task")
        tl.complete_step("s1")
        with pytest.raises(ValueError, match="already terminal"):
            tl.complete_step("s1")

    def test_fail_step(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("s1", "Task")
        step = tl.fail_step("s1", error="oops")
        assert step.status == TaskStepStatus.FAILED
        assert step.error == "oops"

    def test_cancel_step(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("s1", "Task")
        step = tl.cancel_step("s1")
        assert step.status == TaskStepStatus.CANCELLED

    def test_progress_step(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("s1", "Task")
        tl.start_step("s1")
        step = tl.progress_step("s1", result="50% done")
        assert step.result == "50% done"
        assert step.status == TaskStepStatus.IN_PROGRESS  # status unchanged

    def test_progress_non_in_progress_raises(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("s1", "Task")
        with pytest.raises(ValueError, match="only IN_PROGRESS"):
            tl.progress_step("s1")

    def test_revise_step(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("s1", "Old desc")
        step = tl.revise_step("s1", "New desc")
        assert step.description == "New desc"
        assert tl.version == 2  # add + revise

    def test_revise_nonexistent_raises(self) -> None:
        tl = TaskList(session_id="s1")
        with pytest.raises(KeyError, match="not found"):
            tl.revise_step("missing", "x")


# ============================================================================
# TestTaskListStartNext
# ============================================================================


class TestTaskListStartNext:
    def test_start_next_one_pending(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("a", "A")
        step = tl.start_next()
        assert step is not None
        assert step.step_id == "a"
        assert tl.current_step_id == "a"

    def test_start_next_none_pending(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("a", "A")
        tl.complete_step("a")
        assert tl.start_next() is None

    def test_start_next_priority_order(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("low", "Low", priority=10)
        tl.add_step("high", "High", priority=-10)
        step = tl.start_next()
        assert step is not None
        assert step.step_id == "high"

    def test_start_next_empty_list(self) -> None:
        tl = TaskList(session_id="s1")
        assert tl.start_next() is None


# ============================================================================
# TestTaskListOverallProgress
# ============================================================================


class TestTaskListOverallProgress:
    def test_zero_steps(self) -> None:
        tl = TaskList(session_id="s1")
        assert tl.overall_progress == 0.0

    def test_one_completed_of_two(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("a", "A")
        tl.add_step("b", "B")
        tl.complete_step("a")
        assert tl.overall_progress == 0.5

    def test_all_completed(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("a", "A")
        tl.add_step("b", "B")
        tl.complete_step("a")
        tl.complete_step("b")
        assert tl.overall_progress == 1.0

    def test_none_completed(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("a", "A")
        tl.add_step("b", "B")
        assert tl.overall_progress == 0.0

    def test_failed_not_counted_as_completed(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("a", "A")
        tl.add_step("b", "B")
        tl.fail_step("a")
        assert tl.overall_progress == 0.0


# ============================================================================
# TestTaskListQueries
# ============================================================================


class TestTaskListQueries:
    def test_steps_by_status(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("a", "A")
        tl.add_step("b", "B")
        tl.add_step("c", "C")
        tl.complete_step("a")
        tl.start_step("b")
        pending = tl.steps_by_status(TaskStepStatus.PENDING)
        assert len(pending) == 1
        assert pending[0].step_id == "c"

    def test_completed_count(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("a", "A")
        tl.add_step("b", "B")
        tl.complete_step("a")
        assert tl.completed_count == 1

    def test_pending_count(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("a", "A")
        tl.add_step("b", "B")
        tl.add_step("c", "C")
        tl.complete_step("a")
        assert tl.pending_count == 2

    def test_is_fully_completed_true(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("a", "A")
        tl.complete_step("a")
        assert tl.is_fully_completed is True

    def test_is_fully_completed_false_partial(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("a", "A")
        tl.add_step("b", "B")
        tl.complete_step("a")
        assert tl.is_fully_completed is False

    def test_is_fully_completed_empty(self) -> None:
        tl = TaskList(session_id="s1")
        assert tl.is_fully_completed is False

    def test_has_failures_true(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("a", "A")
        tl.fail_step("a")
        assert tl.has_failures is True

    def test_has_failures_false(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("a", "A")
        tl.complete_step("a")
        assert tl.has_failures is False

    def test_get_step(self) -> None:
        tl = TaskList(session_id="s1")
        tl.add_step("x", "X")
        s = tl.get_step("x")
        assert s.step_id == "x"

    def test_updated_at_changes_on_mutation(self) -> None:
        tl = TaskList(session_id="s1")
        v1 = tl.updated_at
        time.sleep(0.05)
        tl.add_step("s1", "A")
        assert tl.updated_at > v1
