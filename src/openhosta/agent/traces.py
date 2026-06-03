"""Observability traces — immutable-append trace records for agent execution.

DEF-TRACE-001 — Immutable-append trace classes with guard metadata

This module defines the building blocks required to reconstruct an audit-grade
execution trace:

1. :class:`GuardMetadata` — declarative execution guardrails (scope, tool
   whitelist, token ceiling, step budget, confirmation policy).
2. :class:`InteractionTrace` — append-only log of human↔agent turns.
3. :class:`WorkspaceActivity` — append-only log of file-system side-effects.
4. :class:`ExecutionTrace` — aggregate container that links the above with
   timing and guard metadata for a single execution unit.

All trace classes use ``frozen=True`` dataclasses to guarantee immutability.
"Append" semantics are achieved by ``append(...)`` methods that *return* a
**new** instance containing the original entries plus the new record.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

# --------------------------------------------------------------------------- #
# GuardMetadata
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class GuardMetadata:
    """Declarative guardrails that bound an execution unit.

    Parameters
    ----------
    scope: str
        Human-readable scope description (e.g. ``"file-system"``).
    allowed_tools: tuple[str, ...]
        Whitelisted tool identifiers. Empty tuple means *all tools allowed*.
    denied_tools: tuple[str, ...]
        Explicitly blacklisted tool identifiers (checked before whitelist).
    max_tokens: int
        Hard token ceiling for this execution unit (``-1`` = unlimited).
    max_steps: int
        Maximum number of discrete steps before forced stop (``-1`` = unlimited).
    required_confirmations: tuple[str, ...]
        Actions that require explicit human confirmation before execution.
    description: str
        Optional free-form guard description.
    """

    scope: str
    allowed_tools: tuple[str, ...] = ()
    denied_tools: tuple[str, ...] = ()
    max_tokens: int = -1
    max_steps: int = -1
    required_confirmations: tuple[str, ...] = ()
    description: str = ""

    # ---- Helpers ----

    def tool_allowed(self, tool_name: str) -> bool:
        """Return ``True`` if *tool_name* passes the guard filter.

        Deny-list is checked *before* allow-list.  An empty allow-list
        means "no restriction".
        """
        if tool_name in self.denied_tools:
            return False
        if self.allowed_tools and tool_name not in self.allowed_tools:
            return False
        return True

    def requires_confirmation(self, action: str) -> bool:
        """Return ``True`` if *action* is in the confirmation whitelist."""
        return action in self.required_confirmations

    @property
    def has_token_limit(self) -> bool:
        """``True`` when a finite token ceiling is set."""
        return self.max_tokens >= 0

    @property
    def has_step_limit(self) -> bool:
        """``True`` when a finite step budget is set."""
        return self.max_steps >= 0


# --------------------------------------------------------------------------- #
# InteractionTrace
# --------------------------------------------------------------------------- #


class TurnRole(Enum):
    """Speaker within a trace turn."""

    HUMAN = auto()
    AGENT = auto()
    SYSTEM = auto()


@dataclass(frozen=True)
class _Turn:
    """Single turn inside an interaction trace.

    Parameters
    ----------
    role: TurnRole
        Who produced this turn.
    content: str
        The textual payload.
    timestamp: float
        Epoch seconds when the turn was recorded.
    metadata: dict[str, Any]
        Optional contextual metadata (e.g. tool-call identifiers).
    """

    role: TurnRole
    content: str
    timestamp: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class InteractionTrace:
    """Immutable-append log of human ↔ agent dialogue turns.

    Parameters
    ----------
    trace_id: str
        Unique identifier for this trace.
    turns: tuple[_Turn, ...]
        Frozen sequence of turns (append-only via :meth:`append_turn`).
    """

    trace_id: str
    turns: tuple[_Turn, ...] = ()

    def append_turn(
        self,
        role: TurnRole,
        content: str,
        timestamp: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> InteractionTrace:
        """Return **new** trace with *content* appended as a turn.

        Parameters
        ----------
        role: TurnRole
            Speaker role.
        content: str
            Turn content.
        timestamp: float | None
            Epoch seconds (defaults to ``time.time()``).
        metadata: dict[str, Any] | None
            Optional contextual metadata.

        Returns
        -------
        InteractionTrace
            New instance containing ``self.turns + (new_turn,)``.
        """
        if timestamp is None:
            timestamp = time.time()
        if metadata is None:
            metadata = {}
        new_turn = _Turn(
            role=role,
            content=content,
            timestamp=timestamp,
            metadata=metadata,
        )
        return InteractionTrace(trace_id=self.trace_id, turns=self.turns + (new_turn,))

    def append_human(self, content: str, metadata: dict[str, Any] | None = None) -> InteractionTrace:
        """Convenience: append a human turn and return new trace."""
        return self.append_turn(TurnRole.HUMAN, content, metadata=metadata)

    def append_agent(self, content: str, metadata: dict[str, Any] | None = None) -> InteractionTrace:
        """Convenience: append an agent turn and return new trace."""
        return self.append_turn(TurnRole.AGENT, content, metadata=metadata)

    def append_system(self, content: str, metadata: dict[str, Any] | None = None) -> InteractionTrace:
        """Convenience: append a system turn and return new trace."""
        return self.append_turn(TurnRole.SYSTEM, content, metadata=metadata)

    @property
    def turn_count(self) -> int:
        """Number of turns in this trace."""
        return len(self.turns)

    @property
    def is_empty(self) -> bool:
        """``True`` when no turns have been recorded."""
        return len(self.turns) == 0


# --------------------------------------------------------------------------- #
# WorkspaceActivity
# --------------------------------------------------------------------------- #


class ActivityKind(Enum):
    """Category of workspace side-effect."""

    FILE_READ = auto()
    FILE_WRITE = auto()
    FILE_CREATE = auto()
    FILE_DELETE = auto()
    DIR_LIST = auto()
    DIR_CREATE = auto()
    DIR_DELETE = auto()
    COMMAND_EXECUTE = auto()
    OTHER = auto()


@dataclass(frozen=True)
class _ActivityRecord:
    """Single workspace activity entry.

    Parameters
    ----------
    kind: ActivityKind
        Category of operation.
    path: str
        File or directory path affected.
    timestamp: float
        Epoch seconds.
    details: dict[str, Any]
        Free-form supplemental information (bytes written, exit code, …).
    """

    kind: ActivityKind
    path: str
    timestamp: float
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WorkspaceActivity:
    """Immutable-append log of workspace side-effects.

    Parameters
    ----------
    activity_id: str
        Unique identifier for this activity log.
    records: tuple[_ActivityRecord, ...]
        Frozen sequence of records (append-only via :meth:`append_record`).
    """

    activity_id: str
    records: tuple[_ActivityRecord, ...] = ()

    def append_record(
        self,
        kind: ActivityKind,
        path: str,
        timestamp: float | None = None,
        details: dict[str, Any] | None = None,
    ) -> WorkspaceActivity:
        """Return **new** workspace activity with *kind*/*path* appended.

        Returns
        -------
        WorkspaceActivity
            New instance with ``self.records + (new_record,)``.
        """
        if timestamp is None:
            timestamp = time.time()
        if details is None:
            details = {}
        new_record = _ActivityRecord(
            kind=kind,
            path=path,
            timestamp=timestamp,
            details=details,
        )
        return WorkspaceActivity(
            activity_id=self.activity_id, records=self.records + (new_record,)
        )

    @property
    def record_count(self) -> int:
        """Number of recorded activities."""
        return len(self.records)

    @property
    def is_empty(self) -> bool:
        """``True`` when no activities have been recorded."""
        return len(self.records) == 0

    def filter_by_kind(self, kind: ActivityKind) -> WorkspaceActivity:
        """Return **new** activity containing only records matching *kind*."""
        filtered = tuple(r for r in self.records if r.kind == kind)
        return WorkspaceActivity(activity_id=self.activity_id, records=filtered)

    def filter_by_path_prefix(self, prefix: str) -> WorkspaceActivity:
        """Return **new** activity whose records touch paths starting with *prefix*."""
        filtered = tuple(r for r in self.records if r.path.startswith(prefix))
        return WorkspaceActivity(activity_id=self.activity_id, records=filtered)


# --------------------------------------------------------------------------- #
# ExecutionTrace
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ExecutionTrace:
    """Aggregate execution trace for a single execution unit.

    Combines interaction dialogue, workspace side-effects, guard metadata,
    timing and an outcome into one immutable container.

    Parameters
    ----------
    execution_id: str
        Unique identifier for this execution unit.
    session_id: str
        Parent session that owns this execution.
    interaction_trace: InteractionTrace
        Dialogue turns for this execution.
    workspace_activity: WorkspaceActivity
        File-system side-effects.
    guard_metadata: GuardMetadata | None
        Guardrails applied during execution (``None`` = no guards).
    started_at: float
        Epoch seconds when execution began.
    ended_at: float | None
        Epoch seconds when execution finished (``None`` = still running).
    outcome: str
        Single-word outcome tag (e.g. ``"success"``, ``"error"``).
    error: str | None
        Error message if outcome is ``"error"``.
    """

    execution_id: str
    session_id: str
    interaction_trace: InteractionTrace
    workspace_activity: WorkspaceActivity
    guard_metadata: GuardMetadata | None = None
    started_at: float = field(default_factory=time.time)
    ended_at: float | None = None
    outcome: str = "running"
    error: str | None = None

    # ---- Mutations return NEW instances ----

    def finish(self, outcome: str, error: str | None = None) -> ExecutionTrace:
        """Return **new** execution trace marked as finished.

        Parameters
        ----------
        outcome: str
            Outcome tag (``"success"``, ``"error"``, ``"timed_out"``, …).
        error: str | None
            Optional error message.

        Returns
        -------
        ExecutionTrace
            New instance with ``ended_at`` set and outcome/error stored.
        """
        return ExecutionTrace(
            execution_id=self.execution_id,
            session_id=self.session_id,
            interaction_trace=self.interaction_trace,
            workspace_activity=self.workspace_activity,
            guard_metadata=self.guard_metadata,
            started_at=self.started_at,
            ended_at=time.time(),
            outcome=outcome,
            error=error,
        )

    def with_interaction(self, interaction_trace: InteractionTrace) -> ExecutionTrace:
        """Return **new** trace with updated :attr:`interaction_trace`."""
        return ExecutionTrace(
            execution_id=self.execution_id,
            session_id=self.session_id,
            interaction_trace=interaction_trace,
            workspace_activity=self.workspace_activity,
            guard_metadata=self.guard_metadata,
            started_at=self.started_at,
            ended_at=self.ended_at,
            outcome=self.outcome,
            error=self.error,
        )

    def with_workspace(self, workspace_activity: WorkspaceActivity) -> ExecutionTrace:
        """Return **new** trace with updated :attr:`workspace_activity`."""
        return ExecutionTrace(
            execution_id=self.execution_id,
            session_id=self.session_id,
            interaction_trace=self.interaction_trace,
            workspace_activity=workspace_activity,
            guard_metadata=self.guard_metadata,
            started_at=self.started_at,
            ended_at=self.ended_at,
            outcome=self.outcome,
            error=self.error,
        )

    @property
    def duration(self) -> float:
        """Elapsed seconds (since start or since end if finished)."""
        end = self.ended_at if self.ended_at is not None else time.time()
        return end - self.started_at

    @property
    def is_finished(self) -> bool:
        """``True`` when ``ended_at`` has been set."""
        return self.ended_at is not None

    @property
    def is_success(self) -> bool:
        """``True`` when finished with ``"success"`` outcome."""
        return self.outcome == "success" and self.is_finished

    @property
    def turn_count(self) -> int:
        """Delegated to :attr:`interaction_trace.turn_count`."""
        return self.interaction_trace.turn_count

    @property
    def activity_count(self) -> int:
        """Delegated to :attr:`workspace_activity.record_count`."""
        return self.workspace_activity.record_count
