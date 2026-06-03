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
    # Interaction

    def get(self, msg: str) -> str:
        """Send a message to the agent session via the capability dispatcher.

        Dispatch order:
        1. ``@router`` capabilities — first successful router decides the path.
        2. ``@planner`` capabilities — first successful planner generates a plan.
        3. ``@playbook`` capabilities — first successful playbook executes the workflow.
        4. ``@infer`` capabilities — first successful inference produces a result.
        5. ``@tool`` capabilities — first successful tool runs.
        6. Fallback to ``AgentEngine.execute_step`` (echoes the message).

        Parameters
        ----------
        msg: str
            The inbound message to dispatch.

        Returns
        -------
        str
            The text result produced by the dispatched capability or the engine fallback.

        Raises
        ------
        RuntimeError
            If the agent has not yet been recruited (status != ``"RECRUITED"``).
        """
        if self.status != "RECRUITED":
            raise RuntimeError("Agent must be recruited first.")

        from openhosta.agent.capability import CapabilityType  # noqa: PLC2701
        from openhosta.agent.dispatch import CapabilityDispatcher  # noqa: PLC2701

        engine = self._ensure_engine()
        session = self._agent_session
        dispatcher = CapabilityDispatcher()

        # Dispatch priority: router > planner > playbook > infer > tool
        priority_order = (
            CapabilityType.ROUTER,
            CapabilityType.PLANNER,
            CapabilityType.PLAYBOOK,
            CapabilityType.INFERENCE,
            CapabilityType.TOOL,
        )

        for cap_type in priority_order:
            results = dispatcher.route_by_type(cap_type, msg=msg)
            for dr in results:
                if dr.success is not None and dr.success:
                    return str(dr.result) if dr.result is not None else ""

        # Fallback: use the engine's execute_step on the agent session
        if session is not None:
            return engine.execute_step(session.session_id, msg)

        return f"response to: {msg}"

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
