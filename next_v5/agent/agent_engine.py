"""Agent engine — multi-session lifecycle management.

Responsible for creation, orchestration, suspension, resumption and
archiving of agent sessions.
"""

from __future__ import annotations

import threading
import uuid
from typing import Any

from .agent_session import AgentSession
from .agent_status import AgentStatus


class AgentEngine:
    """Multi-session agent lifecycle engine.

    Parameters
    ----------
    model: str
        Default model identifier for newly created sessions.
    base_url: str
        Default API endpoint for newly created sessions.
    """

    def __init__(self, model: str, base_url: str) -> None:
        self.model = model
        self.base_url = base_url
        self._sessions: dict[str, AgentSession] = {}
        self._lock = threading.Lock()
        self._archives: list[AgentSession] = []

    # ---- CRUD sessions ----

    def create_session(
        self,
        title: str,
        role: str,
        tags: list[str] | None = None,
        timeout: float = 600.0,
        tokens_limit: int = 256_000,
    ) -> AgentSession:
        """Create and register a new agent session.

        Parameters
        ----------
        title: str
            Human-readable title.
        role: str
            Agent role.
        tags: list[str] | None
            Optional metadata tags.
        timeout: float
            Max execution time in seconds.
        tokens_limit: int
            Hard token ceiling.

        Returns
        -------
        AgentSession
            The freshly created session.
        """
        session_id = str(uuid.uuid4())
        session = AgentSession(
            session_id=session_id,
            title=title,
            role=role,
            model=self.model,
            timeout_seconds=timeout,
            tokens_limit=tokens_limit,
            tags=tags if tags is not None else [],
        )
        with self._lock:
            self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> AgentSession:
        """Retrieve a session by its ID.

        Raises
        ------
        KeyError
            If the session does not exist.
        """
        # Read-only lock not needed for dict get in CPython (GIL protects it),
        # but we use the lock for conceptual consistency.
        with self._lock:
            if session_id not in self._sessions:
                raise KeyError(f"Session {session_id} not found")
            return self._sessions[session_id]

    def list_sessions(
        self, status: AgentStatus | None = None
    ) -> list[AgentSession]:
        """List all sessions, optionally filtered by status.

        Parameters
        ----------
        status: AgentStatus | None
            If provided, only sessions with this status are returned.

        Returns
        -------
        list[AgentSession]
        """
        with self._lock:
            if status is None:
                return list(self._sessions.values())
            return [s for s in self._sessions.values() if s.status == status]

    def pause_session(self, session_id: str) -> AgentSession:
        """Pause a running session.

        Raises
        ------
        KeyError
            If the session does not exist.
        ValueError
            If the session cannot transition to PAUSED.
        """
        session = self.get_session(session_id)
        session.transition_to(AgentStatus.PAUSED)
        return session

    def resume_session(self, session_id: str) -> AgentSession:
        """Resume a paused session.

        Raises
        ------
        KeyError
            If the session does not exist.
        ValueError
            If the session cannot transition to RUNNING.
        """
        session = self.get_session(session_id)
        session.transition_to(AgentStatus.RUNNING)
        return session

    def delete_session(self, session_id: str, archive: bool = True) -> None:
        """Remove a session from the active registry.

        Parameters
        ----------
        session_id: str
            The session to remove.
        archive: bool
            If ``True``, the session is kept in the internal archive list.
        """
        with self._lock:
            session = self._sessions.pop(session_id, None)
            if session is None:
                raise KeyError(f"Session {session_id} not found")
            if archive:
                self._archives.append(session)

    # ---- Metrics ----

    def healthy_sessions(self) -> list[AgentSession]:
        """Return sessions whose utilization < 75 % and are not terminal."""
        with self._lock:
            return [s for s in self._sessions.values() if s.is_healthy()]

    def critical_sessions(self) -> list[AgentSession]:
        """Return sessions with utilization between 75 % and 90 %."""
        with self._lock:
            return [s for s in self._sessions.values() if s.is_critical]

    def saturated_sessions(self) -> list[AgentSession]:
        """Return sessions with utilization >= 90 %."""
        with self._lock:
            return [s for s in self._sessions.values() if s.is_saturated]

    @property
    def session_count(self) -> int:
        """Total number of active sessions."""
        with self._lock:
            return len(self._sessions)

    @property
    def archive_count(self) -> int:
        """Total number of archived sessions."""
        with self._lock:
            return len(self._archives)

    # ---- Orchestration ----

    def send_message(self, session_id: str, message: str) -> str | None:
        """Send a message to a session and transition it to RUNNING.

        This is a placeholder that performs the state transition.
        Actual inference is handled by higher-level components.

        Parameters
        ----------
        session_id: str
            Target session ID.
        message: str
            The message to deliver.

        Returns
        -------
        str | None
            ``"delivered"`` on success, ``None`` if the session cannot accept
            messages (already terminal or unknown).

        Raises
        ------
        KeyError
            If the session does not exist.
        """
        session = self.get_session(session_id)

        # Terminal sessions cannot receive messages
        if session.status.is_terminal:
            return None

        # Transition to RUNNING if possible
        if session.status != AgentStatus.RUNNING:
            try:
                session.transition_to(AgentStatus.RUNNING)
            except ValueError:
                return None

        # Simulate token cost of the message (rough estimate: 1 token per word)
        estimated_tokens = len(message.split())
        session.tokens_used += estimated_tokens

        return "delivered"

    def broadcast(
        self, message: str, status_filter: AgentStatus | None = None
    ) -> int:
        """Send *message* to all matching sessions.

        Parameters
        ----------
        message: str
            The broadcast message.
        status_filter: AgentStatus | None
            If provided, only sessions with this status receive the message.

        Returns
        -------
        int
            Number of sessions that successfully received the message.
        """
        sessions = self.list_sessions(status=status_filter)
        delivered = 0
        for session in sessions:
            result = self.send_message(session.session_id, message)
            if result is not None:
                delivered += 1
        return delivered

    def update_config(self, session_id: str, **kwargs: Any) -> AgentSession:
        """Update configurable attributes of a session.

        Allowed keys: ``model``, ``timeout_seconds``, ``tokens_limit``,
        ``tags``, ``title``.

        Returns
        -------
        AgentSession
            The updated session.

        Raises
        ------
        KeyError
            If the session does not exist.
        """
        session = self.get_session(session_id)
        allowed_keys = {
            "model",
            "timeout_seconds",
            "tokens_limit",
            "tags",
            "title",
        }
        for key, value in kwargs.items():
            if key in allowed_keys:
                setattr(session, key, value)
        return session
