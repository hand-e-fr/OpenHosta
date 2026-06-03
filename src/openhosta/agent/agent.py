"""Public Agent class — high-level lifecycle wrapper around AgentEngine / AgentSession."""

from __future__ import annotations

import inspect
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

        # Build per-agent capability registry by scanning class methods
        from openhosta.agent.capability import CapabilityRegistration, _default_registry  # noqa: PLC2701
        self._registry = CapabilityRegistration()
        # Collect class method names (Agent's "virtual body")
        class_method_names: set[str] = set()
        for name, attr in vars(self.__class__).items():
            if callable(attr) and hasattr(attr, "_capability"):
                class_method_names.add(attr._capability.name)
        # Merge global default registry, replacing class methods with bound versions
        for func, meta in _default_registry.list_all():
            if meta.name in class_method_names:
                # Replace with bound method so dispatcher calls self.func(...)
                bound = getattr(self, func.__name__, func)
                if callable(bound) and hasattr(bound, '__self__'):
                    self._registry.register(bound, meta)
                else:
                    self._registry.register(func, meta)
            else:
                self._registry.register(func, meta)
        # Add class methods not already registered (e.g. @model.infer which doesn't use _default_registry)
        for name, attr in vars(self.__class__).items():
            if callable(attr) and hasattr(attr, "_capability"):
                existing = self._registry.find_by_name(attr._capability.name)
                if existing is None:
                    bound = getattr(self, attr.__name__, attr)
                    if callable(bound) and hasattr(bound, '__self__'):
                        self._registry.register(bound, attr._capability)
                    else:
                        self._registry.register(attr, attr._capability)

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

        # Register backend as default for inference capabilities
        if self._backend is not None:
            from openhosta.agent._config import set_default_backend  # noqa: PLC2701
            from openhosta.backend import BackendSelector  # noqa: PLC2701

            if isinstance(self._backend, BackendSelector):
                resolved = self._backend.resolve()
            else:
                resolved = self._backend
            set_default_backend(resolved)

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
        dispatcher = CapabilityDispatcher(registry=self._registry)

    # Dispatch priority: router > planner > playbook > infer > tool
        priority_order = (
            (CapabilityType.ROUTER, True),
            (CapabilityType.PLANNER, True),
            (CapabilityType.PLAYBOOK, False),
            (CapabilityType.INFERENCE, True),
            (CapabilityType.TOOL, False),
        )

        # Resolve backend for inference-capable types
        from openhosta.backend import BackendSelector  # noqa: PLC2701

        resolved_backend = None
        if self._backend is not None:
            if isinstance(self._backend, BackendSelector):
                resolved_backend = self._backend.resolve()
            else:
                resolved_backend = self._backend

        for cap_type, needs_backend in priority_order:
            if needs_backend and resolved_backend is not None:
                kwargs = {"msg": msg, "_backend": resolved_backend}
            else:
                kwargs = {"msg": msg}

            results = dispatcher.route_by_type(cap_type, **kwargs)
            for dr in results:
                if dr.success is not None and dr.success:
                    result_str = str(dr.result) if dr.result is not None else ""
                    # Interpret router decisions: "route:tag" → dispatch to tagged capabilities
                    if cap_type == CapabilityType.ROUTER and result_str.startswith("route:"):
                        target_tag = result_str.split(":", 1)[1].strip()
                        routed = dispatcher.route_by_tag(target_tag, **kwargs)
                        for r2 in routed:
                            if r2.success is not None and r2.success:
                                return str(r2.result) if r2.result is not None else ""
                        # Router target not found or failed → fall through
                        continue
                    return result_str

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
