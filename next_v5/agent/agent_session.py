"""Agent session — represents a single agent instance with its lifecycle.

State transition rules (defined by ``AgentStatus.valid_transitions``)::

    IDLE → RUNNING              (on send_message)
    RUNNING → IDLE              (on response received)
    RUNNING → PAUSED            (on pause_session)
    PAUSED → RUNNING            (on resume_session)
    RUNNING → WAITING           (on human-in-the-loop request)
    WAITING → RUNNING           (on input received)
    * → TERMINATED              (on successful completion)
    * → FAILED                  (on non-recoverable error)
    RUNNING → TIMED_OUT         (on timeout)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .agent_status import AgentStatus


@dataclass
class AgentSession:
    """Represents a single agent session with lifecycle tracking.

    Parameters
    ----------
    session_id: str
        Unique identifier for this session.
    title: str
        Human-readable title.
    role: str
        Agent role (e.g. ``"ingenieur"``, ``"chef-de-projet"``).
    status: AgentStatus
        Current lifecycle state (default: IDLE).
    tokens_used: int
        Number of tokens consumed so far (default: 0).
    tokens_limit: int
        Hard token ceiling (default: 256 000).
    age_seconds: float
        Elapsed wall-clock seconds since creation (auto-updated via :meth:`tick_age`).
    created_at: float
        Epoch timestamp of creation.
    last_activity: float
        Epoch timestamp of last meaningful activity.
    model: str
        Model identifier used by this session.
    timeout_seconds: float
        Maximum execution time in seconds (default: 600).
    tags: list[str]
        Arbitrary metadata tags.
    """

    session_id: str
    title: str
    role: str
    status: AgentStatus = AgentStatus.IDLE

    # Metrics
    tokens_used: int = 0
    tokens_limit: int = 256_000
    age_seconds: float = 0.0
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)

    # Configuration
    model: str = ""
    timeout_seconds: float = 600.0
    tags: list[str] = field(default_factory=list)

    # ---- State transitions ----

    def transition_to(self, new_status: AgentStatus) -> None:
        """Transition the session to *new_status*.

        Raises
        ------
        ValueError
            If the transition is not allowed by the state machine.
        """
        if not self.status.can_transition_to(new_status):
            raise ValueError(
                f"Invalid transition: {self.status.name} -> {new_status.name}"
                f" for session {self.session_id}"
            )
        self.status = new_status
        self.last_activity = time.time()

    def tick_age(self) -> float:
        """Update ``age_seconds`` and ``last_activity`` to current time.

        Returns
        -------
        float
            Updated age in seconds.
        """
        self.age_seconds = time.time() - self.created_at
        self.last_activity = time.time()
        return self.age_seconds

    # ---- Health checks ----

    def is_healthy(self) -> bool:
        """Return ``True`` if the session is within healthy bounds.

        A session is healthy when:
        - Utilization ratio < 75 %
        - Age is below timeout
        - Status is not terminal
        """
        if self.status.is_terminal:
            return False
        if self.status == AgentStatus.FAILED:
            return False
        if self.utilization_ratio() >= 0.75:
            return False
        if self.age_seconds >= self.timeout_seconds:
            return False
        return True

    def utilization_ratio(self) -> float:
        """Return the fraction of tokens consumed.

        Returns
        -------
        float
            Value in [0, 1]. Values > 1 indicate overflow.
        """
        if self.tokens_limit <= 0:
            return 1.0
        return self.tokens_used / self.tokens_limit

    @property
    def is_saturated(self) -> bool:
        """Return ``True`` if token usage >= 90 %."""
        return self.utilization_ratio() >= 0.90

    @property
    def is_critical(self) -> bool:
        """Return ``True`` if token usage >= 75 % and < 90 %."""
        ratio = self.utilization_ratio()
        return 0.75 <= ratio < 0.90
