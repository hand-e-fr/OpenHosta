"""Canonical execution events for OpenHosta V5 observability.

DEF-EXEC-EVENT-001 — Canonical event types for task, trace and metric emission

Every noteworthy state transition within an agent session or task list emits
a strongly-typed :class:`Event`.  The event taxonomy is:

TaskList lifecycle
------------------
- ``tasklist.created``   — new task list instantiated
- ``tasklist.updated``   — generic state change (version bump)
- ``tasklist.revised``   — step description / metadata revised

Task lifecycle
--------------
- ``task.started``      — a step transitions to IN_PROGRESS
- ``task.progressed``   — intermediate progress reported
- ``task.completed``    — step reached COMPLETED state
- ``task.failed``       — step reached FAILED state
- ``task.cancelled``    — step cancelled manually

Observability
-------------
- ``incident.recorded`` — runtime incident / anomaly captured
- ``metric.recorded``   — numerical metric emitted (tokens, latency, …)
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

# --------------------------------------------------------------------------- #
# EventType
# --------------------------------------------------------------------------- #


class EventType(Enum):
    """Canonical event taxonomy."""

    TASKLIST_CREATED = auto()
    """New task list instantiated."""

    TASKLIST_UPDATED = auto()
    """Generic task list state change (version bumped)."""

    TASKLIST_REVIDED = auto()
    """Step description or metadata revised."""

    TASK_STARTED = auto()
    """A step transitioned to IN_PROGRESS."""

    TASK_PROGRESSED = auto()
    """Intermediate progress reported on an active step."""

    TASK_COMPLETED = auto()
    """A step reached COMPLETED state."""

    TASK_FAILED = auto()
    """A step reached FAILED state."""

    TASK_CANCELLED = auto()
    """A step was cancelled manually."""

    INCIDENT_RECORDED = auto()
    """Runtime incident or anomaly captured."""

    METRIC_RECORDED = auto()
    """Numerical metric emitted."""


# --------------------------------------------------------------------------- #
# Event
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Event:
    """Immutable canonical event emitted during execution.

    Parameters
    ----------
    event_type: EventType
        The taxonomy of this event.
    event_id: str
        Globally unique event identifier.
    timestamp: float
        Epoch seconds of event creation.
    session_id: str
        Parent session identifier.
    tasklist_id: str | None
        Associated task list identifier (if applicable).
    step_id: str | None
        Associated step identifier (if applicable).
    payload: dict[str, Any]
        Free-form structured data specific to the event type.
    metadata: dict[str, Any]
        Cross-cutting context (correlation_id, trace_id, agent version, …).
    """

    event_type: EventType
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    session_id: str = ""
    tasklist_id: str | None = None
    step_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def with_metadata(self, **kwargs: Any) -> Event:
        """Return **new** event with merged metadata entries.

        Existing keys are overwritten by *kwargs*.
        """
        merged = {**self.metadata, **kwargs}
        return Event(
            event_type=self.event_type,
            event_id=self.event_id,
            timestamp=self.timestamp,
            session_id=self.session_id,
            tasklist_id=self.tasklist_id,
            step_id=self.step_id,
            payload=self.payload,
            metadata=merged,
        )

    @property
    def is_task_event(self) -> bool:
        """``True`` for task lifecycle events (started, progressed, …)."""
        return self.event_type in (
            EventType.TASK_STARTED,
            EventType.TASK_PROGRESSED,
            EventType.TASK_COMPLETED,
            EventType.TASK_FAILED,
            EventType.TASK_CANCELLED,
        )

    @property
    def is_tasklist_event(self) -> bool:
        """``True`` for tasklist lifecycle events."""
        return self.event_type in (
            EventType.TASKLIST_CREATED,
            EventType.TASKLIST_UPDATED,
            EventType.TASKLIST_REVIDED,
        )

    @property
    def is_terminal_task_event(self) -> bool:
        """``True`` when the event signals a terminal task outcome."""
        return self.event_type in (
            EventType.TASK_COMPLETED,
            EventType.TASK_FAILED,
            EventType.TASK_CANCELLED,
        )

    @property
    def is_positive(self) -> bool:
        """``True`` if the event indicates a positive outcome."""
        return self.event_type in (
            EventType.TASK_COMPLETED,
            EventType.TASK_STARTED,
            EventType.TASK_PROGRESSED,
            EventType.TASKLIST_CREATED,
            EventType.TASKLIST_UPDATED,
        )


# --------------------------------------------------------------------------- #
# EventStream
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class EventStream:
    """Immutable-append ordered list of :class:`Event`\\s.

    Provides filtering and lookup utilities for replay and audit scenarios.

    Parameters
    ----------
    stream_id: str
        Identifier for this event stream.
    events: tuple[Event, ...]
        Frozen sequence of events.
    """

    stream_id: str
    events: tuple[Event, ...] = ()

    def append(self, event: Event) -> EventStream:
        """Return **new** stream with *event* appended.

        Returns
        -------
        EventStream
            New instance containing ``self.events + (event,)``.
        """
        return EventStream(stream_id=self.stream_id, events=self.events + (event,))

    def filter_by_type(self, event_type: EventType) -> EventStream:
        """Return **new** stream containing only events of *event_type*."""
        filtered = tuple(e for e in self.events if e.event_type == event_type)
        return EventStream(stream_id=self.stream_id, events=filtered)

    def filter_by_session(self, session_id: str) -> EventStream:
        """Return **new** stream for a specific *session_id*."""
        filtered = tuple(e for e in self.events if e.session_id == session_id)
        return EventStream(stream_id=self.stream_id, events=filtered)

    def filter_by_step(self, step_id: str) -> EventStream:
        """Return **new** stream for a specific *step_id*."""
        filtered = tuple(e for e in self.events if e.step_id == step_id)
        return EventStream(stream_id=self.stream_id, events=filtered)

    @property
    def count(self) -> int:
        """Number of events in the stream."""
        return len(self.events)

    @property
    def is_empty(self) -> bool:
        """``True`` when no events have been recorded."""
        return len(self.events) == 0

    @property
    def last_event(self) -> Event | None:
        """The most recent event, or ``None`` if empty."""
        if not self.events:
            return None
        return self.events[-1]
