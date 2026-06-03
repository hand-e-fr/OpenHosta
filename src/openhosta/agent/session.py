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
from collections.abc import Generator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from openhosta.agent.status import AgentStatus

if TYPE_CHECKING:
    from openhosta.agent.engine import AgentEngine


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
    engine: AgentEngine | None = None
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

    # ---- Streaming ----

    def get_stream(
        self, message: str, interval_ms: int = 100
    ) -> Generator[str, None, None]:
        """Yield text chunks as the engine processes *message*.

        The session must be in RUNNING state.  The engine's
        :meth:`AgentEngine.execute_step` is called to obtain the full
        response, which is then sliced into chunks of *interval_ms*
        character-width segments.

        Parameters
        ----------
        message: str
            The message to process.
        interval_ms: int
            Character-width of each chunk (derived from the interval).
            Defaults to 100 characters.

        Yields
        ------
        str
            Chunks of response text.

        Raises
        ------
        RuntimeError
            If the session is not in RUNNING state or the engine
            reference is missing.
        """
        if self.status != AgentStatus.RUNNING:
            raise RuntimeError("Session must be RUNNING")
        if self.engine is None:
            raise RuntimeError("Session has no engine reference")

        full_response = self.engine.execute_step(self.session_id, message)
        chunk_size = max(1, interval_ms)
        pos = 0
        while pos < len(full_response):
            yield full_response[pos : pos + chunk_size]
            pos += chunk_size
