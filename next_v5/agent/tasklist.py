"""TaskList — mutable state container for an ordered list of execution steps.

DEF-TASKLIST-STATE-001 — TaskList state management with version tracking

The TaskList tracks the progress of a multi-step plan within a single agent
session.  It exposes:

- **``session_id``** — parent session identifier.
- **``version``** — monotonically increasing counter bumped on *every*
  state mutation (append, complete, cancel, revise).
- **``current_step_id``** — the step that is currently active.
- **``steps``** — ordered list of :class:`TaskStep` objects.
- **``overall_progress``** — computed ratio of completed steps
  (0.0 = nothing done, 1.0 = all steps finished).
- **``updated_at``** — epoch timestamp of the last mutation.

The class follows a *snapshot* model: read-only properties such as
``overall_progress`` and ``version`` are derived from internal state,
never set directly.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto

# --------------------------------------------------------------------------- #
# TaskStepStatus
# --------------------------------------------------------------------------- #


class TaskStepStatus(Enum):
    """Lifecycle state of a single task step."""

    PENDING = auto()
    """Queued, not yet started."""

    IN_PROGRESS = auto()
    """Currently being executed."""

    COMPLETED = auto()
    """Finished successfully."""

    FAILED = auto()
    """Failed with an error."""

    CANCELLED = auto()
    """Manually cancelled before completion."""


# --------------------------------------------------------------------------- #
# TaskStep
# --------------------------------------------------------------------------- #


@dataclass
class TaskStep:
    """Single step within a :class:`TaskList`.

    Parameters
    ----------
    step_id: str
        Unique step identifier within this task list.
    description: str
        Human-readable description of the work to be done.
    status: TaskStepStatus
        Current lifecycle state (default: ``PENDING``).
    priority: int
        Execution priority (lower = higher priority; default: 0).
    created_at: float
        Epoch timestamp of creation.
    completed_at: float | None
        Epoch timestamp when step reached a terminal state.
    result: str | None
        Optional short summary produced upon completion.
    error: str | None
        Optional error message upon failure.
    """

    step_id: str
    description: str
    status: TaskStepStatus = TaskStepStatus.PENDING
    priority: int = 0
    created_at: float = field(default_factory=time.time)
    completed_at: float | None = None
    result: str | None = None
    error: str | None = None

    @property
    def is_terminal(self) -> bool:
        """``True`` when the step has reached a non-reversible state."""
        return self.status in (
            TaskStepStatus.COMPLETED,
            TaskStepStatus.FAILED,
            TaskStepStatus.CANCELLED,
        )

    @property
    def is_active(self) -> bool:
        """``True`` when the step is currently being executed."""
        return self.status == TaskStepStatus.IN_PROGRESS


# --------------------------------------------------------------------------- #
# TaskList
# --------------------------------------------------------------------------- #


@dataclass
class TaskList:
    """Ordered list of execution steps tied to an agent session.

    Parameters
    ----------
    session_id: str
        Parent session identifier.
    title: str
        Human-readable title for this task list.
    steps: list[TaskStep]
        Ordered list of steps (mutable; operations bump version).
    version: int
        Monotonically increasing revision counter.
    current_step_id: str | None
        The step currently being worked on (``None`` = idle).
    overall_progress: float
        Derived ratio of completed steps (auto-computed on read).
    updated_at: float
        Epoch timestamp of last mutation.
    """

    session_id: str
    title: str = ""
    steps: list[TaskStep] = field(default_factory=list)
    version: int = 0
    current_step_id: str | None = None
    updated_at: float = field(default_factory=time.time)

    # ---- Auto-computed read-only property ----

    @property
    def overall_progress(self) -> float:
        """Return fraction of completed steps in [0.0, 1.0].

        Returns 0.0 when no steps exist (nothing to do = 0% done).
        """
        if not self.steps:
            return 0.0
        completed = sum(1 for s in self.steps if s.status == TaskStepStatus.COMPLETED)
        return completed / len(self.steps)

    # ---- Internals ----

    def _bump(self) -> None:
        """Increment version and refresh updated_at."""
        self.version += 1
        self.updated_at = time.time()

    # ---- Public mutation API ----

    def add_step(
        self,
        step_id: str,
        description: str,
        priority: int = 0,
    ) -> TaskStep:
        """Append a new pending step and return it.

        Raises
        ------
        ValueError
            If *step_id* already exists in this task list.
        """
        if any(s.step_id == step_id for s in self.steps):
            raise ValueError(f"Step '{step_id}' already exists in task list")
        step = TaskStep(step_id=step_id, description=description, priority=priority)
        self.steps.append(step)
        self._bump()
        return step

    def complete_step(self, step_id: str, result: str | None = None) -> TaskStep:
        """Mark *step_id* as COMPLETED.

        Raises
        ------
        KeyError
            If *step_id* is not found.
        ValueError
            If the step is already in a terminal state.
        """
        step = self._find_step(step_id)
        if step.is_terminal:
            raise ValueError(f"Step '{step_id}' is already terminal ({step.status.name})")
        step.status = TaskStepStatus.COMPLETED
        step.completed_at = time.time()
        step.result = result
        if self.current_step_id == step_id:
            self.current_step_id = self._next_pending_step_id()
        self._bump()
        return step

    def fail_step(self, step_id: str, error: str | None = None) -> TaskStep:
        """Mark *step_id* as FAILED.

        Raises
        ------
        KeyError
            If *step_id* is not found.
        ValueError
            If the step is already in a terminal state.
        """
        step = self._find_step(step_id)
        if step.is_terminal:
            raise ValueError(f"Step '{step_id}' is already terminal ({step.status.name})")
        step.status = TaskStepStatus.FAILED
        step.completed_at = time.time()
        step.error = error
        if self.current_step_id == step_id:
            self.current_step_id = self._next_pending_step_id()
        self._bump()
        return step

    def cancel_step(self, step_id: str) -> TaskStep:
        """Mark *step_id* as CANCELLED.

        Raises
        ------
        KeyError
            If *step_id* is not found.
        ValueError
            If the step is already in a terminal state.
        """
        step = self._find_step(step_id)
        if step.is_terminal:
            raise ValueError(f"Step '{step_id}' is already terminal ({step.status.name})")
        step.status = TaskStepStatus.CANCELLED
        step.completed_at = time.time()
        if self.current_step_id == step_id:
            self.current_step_id = self._next_pending_step_id()
        self._bump()
        return step

    def start_step(self, step_id: str) -> TaskStep:
        """Mark *step_id* as IN_PROGRESS and set it as current step.

        Raises
        ------
        KeyError
            If *step_id* is not found.
        ValueError
            If the step is not PENDING.
        """
        step = self._find_step(step_id)
        if step.status != TaskStepStatus.PENDING:
            raise ValueError(
                f"Step '{step_id}' is {step.status.name}; only PENDING steps can be started"
            )
        step.status = TaskStepStatus.IN_PROGRESS
        self.current_step_id = step_id
        self._bump()
        return step

    def progress_step(self, step_id: str, result: str | None = None) -> TaskStep:
        """Record intermediate progress on an IN_PROGRESS step.

        This does *not* change the step status; it merely updates the
        ``result`` field (useful for incremental status messages).

        Raises
        ------
        KeyError
            If *step_id* is not found.
        """
        step = self._find_step(step_id)
        if step.status != TaskStepStatus.IN_PROGRESS:
            raise ValueError(
                f"Step '{step_id}' is {step.status.name}; "
                f"only IN_PROGRESS steps can be progressed"
            )
        if result is not None:
            step.result = result
        self._bump()
        return step

    def revise_step(self, step_id: str, description: str) -> TaskStep:
        """Update the description of an existing step.

        Raises
        ------
        KeyError
            If *step_id* is not found.
        """
        step = self._find_step(step_id)
        step.description = description
        self._bump()
        return step

    def start_next(self) -> TaskStep | None:
        """Auto-start the first PENDING step (by priority, then creation order).

        Returns the started step, or ``None`` if no pending steps exist.
        """
        next_id = self._next_pending_step_id()
        if next_id is None:
            return None
        return self.start_step(next_id)

    # ---- Query helpers ----

    def get_step(self, step_id: str) -> TaskStep:
        """Retrieve a step by ID. Raises ``KeyError`` if absent."""
        return self._find_step(step_id)

    def steps_by_status(self, status: TaskStepStatus) -> list[TaskStep]:
        """Return steps matching *status* (preserves insertion order)."""
        return [s for s in self.steps if s.status == status]

    @property
    def total_steps(self) -> int:
        """Total number of steps."""
        return len(self.steps)

    @property
    def completed_count(self) -> int:
        """Number of COMPLETED steps."""
        return sum(1 for s in self.steps if s.status == TaskStepStatus.COMPLETED)

    @property
    def pending_count(self) -> int:
        """Number of PENDING steps."""
        return sum(1 for s in self.steps if s.status == TaskStepStatus.PENDING)

    @property
    def is_fully_completed(self) -> bool:
        """``True`` when every step is COMPLETED."""
        return bool(
            self.steps
            and all(s.status == TaskStepStatus.COMPLETED for s in self.steps)
        )

    @property
    def has_failures(self) -> bool:
        """``True`` when at least one step is FAILED."""
        return any(s.status == TaskStepStatus.FAILED for s in self.steps)

    # ---- private helpers ----

    def _find_step(self, step_id: str) -> TaskStep:
        for s in self.steps:
            if s.step_id == step_id:
                return s
        raise KeyError(f"Step '{step_id}' not found in task list")

    def _next_pending_step_id(self) -> str | None:
        """Return the step_id of the first pending step (priority then order)."""
        pending = [s for s in self.steps if s.status == TaskStepStatus.PENDING]
        if not pending:
            return None
        pending.sort(key=lambda s: s.priority)
        return pending[0].step_id
