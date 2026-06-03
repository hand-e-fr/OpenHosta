"""Public Agent class — high-level lifecycle wrapper around AgentEngine / AgentSession."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openhosta.agent.engine import AgentEngine
    from openhosta.agent.session import AgentSession
    from openhosta.backend import BackendModel, BackendSelector
    from openhosta.workspace import Workspace


class Agent:
    """Héritable agent public avec cycle de vie CONFIGURED → RECRUITED → FREED / KILLED.

    Encapsule un AgentEngine (création de sessions) et un AgentSession unique
    pour exposer une API simple en phase 2.
    """

    def __init__(
        self,
        backend: BackendModel | BackendSelector | None = None,
        workspace: Workspace | None = None,
        learning: bool = False,
        reincarn: bool = False,
    ) -> None:
        # Class-level backend from @compile decorator
        if backend is None:
            backend = getattr(self.__class__, "_backend", None)  # type: ignore[attr-defined]

        self._backend = backend
        self._learning = learning
        self._reincarn = reincarn
        self._workspace_provided = workspace
        self._agent_session: AgentSession | None = None
        self._agent_engine: AgentEngine | None = None
        self.status = "CONFIGURED"
        self.notes: list[str] = []

    # ------------------------------------------------------------------
    # Lifecycle

    def _ensure_engine(self) -> AgentEngine:
        """Lazy-create AgentEngine from backend if needed."""
        if self._agent_engine is not None:
            return self._agent_engine

        from openhosta.agent.engine import AgentEngine  # noqa: PLC2701
        from openhosta.backend import BackendSelector  # noqa: PLC2701

        if self._backend is None:
            self._agent_engine = AgentEngine(model="default", base_url="http://localhost:8000/v1")
            return self._agent_engine

        if isinstance(self._backend, BackendSelector):
            resolved = self._backend.resolve()
        else:
            resolved = self._backend  # BackendModel

        self._agent_engine = AgentEngine(
            model=resolved.model_name,
            base_url=resolved.base_url,
        )
        return self._agent_engine

    def recruit(self, quota: int | None = None) -> Agent:
        """Create a session, transition to RECRUITED.

        Parameters
        ----------
        quota: int | None
            Reserved token budget for this session (unused — future).

        Returns
        -------
        Self for chaining.
        """
        if self.status != "CONFIGURED":
            raise RuntimeError(
                f"Cannot recruit: agent is already in {self.status!r} state."
            )
        engine = self._ensure_engine()
        self._agent_session = engine.create_session(
            title=self.__class__.__name__,
            role="agent",
        )
        if quota is not None:
            self._agent_session.tokens_limit = quota
        self.status = "RECRUITED"
        return self

    def free(self) -> str:
        """Finalize the session cleanly.

        Returns
        -------
        Empty string (final report is planned for Phase 3).
        """
        if self.status not in ("RECRUITED",):
            raise RuntimeError(
                f"Cannot free: agent is in {self.status!r} state."
            )

        session = self._agent_session
        if session is not None:
            from openhosta.agent.status import AgentStatus  # noqa: PLC2701

            try:
                session.transition_to(AgentStatus.TERMINATED)
            except ValueError:
                pass

        self.status = "FREED"
        return ""

    def kill(self) -> None:
        """Kill the session immediately (no cleanup)."""
        session = self._agent_session
        if session is not None:
            from openhosta.agent.status import AgentStatus  # noqa: PLC2701

            try:
                session.transition_to(AgentStatus.FAILED)
            except ValueError:
                pass

        self.status = "KILLED"

    # ------------------------------------------------------------------
    # Interaction stub (Phase 3)

    def get(self, msg: str) -> str:
        """Send a message to the agent session.

        Stub — to be implemented in Phase 3.
        """
        raise NotImplementedError("Agent.get() will be implemented in Phase 3")

    # ------------------------------------------------------------------
    # Properties

    @property
    def workspace(self) -> Workspace:
        if self._workspace_provided is not None:
            return self._workspace_provided
        from openhosta.workspace import Workspace  # noqa: PLC2701

        return Workspace(Path("."))

    @property
    def learning(self) -> bool:
        return self._learning

    @property
    def reincarn(self) -> bool:
        return self._reincarn

    @property
    def agent_session(self) -> AgentSession | None:
        return self._agent_session

    @property
    def agent_engine(self) -> AgentEngine | None:
        return self._agent_engine
