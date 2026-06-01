"""OpenHosta V5 — Agent core sub-package.

Public API
----------
- :class:`AgentStatus` — lifecycle state enumeration
- :class:`AgentSession` — single session with state machine
- :class:`AgentEngine` — multi-session CRUD and metrics
- :class:`CapabilityType` — capability categorisation enum
- :class:`CapabilityMetadata` — frozen metadata container
- :class:`CapabilityRegistration` — global auto-registration registry
- :func:`tool` — decorator for deterministic tool capabilities
- :func:`infer` — decorator for LLM-powered inference capabilities
- :func:`playbook` — decorator for multi-step orchestrations
- :func:`planner` — decorator for goal-decomposition capabilities
- :func:`router` — decorator for routing-decision capabilities
- :class:`DispatchResult` — dispatch outcome container
- :class:`CapabilityDispatcher` — look-up, route and execute capabilities

Phase 3 — Observability
~~~~~~~~~~~~~~~~~~~~~~~~
- :class:`GuardMetadata` — declarative execution guardrails
- :class:`TurnRole` — speaker role in interaction traces
- :class:`InteractionTrace` — immutable-append dialogue trace
- :class:`ActivityKind` — workspace operation category enum
- :class:`WorkspaceActivity` — immutable-append workspace side-effect log
- :class:`ExecutionTrace` — aggregate execution trace container
- :class:`TaskStepStatus` — lifecycle state of a single task step
- :class:`TaskStep` — single step within a task list
- :class:`TaskList` — ordered step list with version tracking
- :class:`EventType` — canonical event taxonomy enum
- :class:`Event` — immutable canonical event record
- :class:`EventStream` — immutable-append ordered event list

Phase 4 — Auto-Healing, Roles, Downstream
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- :class:`GuardConfig` — declarative healing guardrails
- :class:`HealingState` — mutable runtime healing tracker
- :class:`HealingHook` — extensible hook base class
- :class:`HealingResult` — encapsulated healing outcome
- :class:`Healer` — retry orchestrator with fuzzy fallback
- :func:`heal` — one-shot convenience healing function
- :class:`Principal` — authenticated identity with role bindings
- :class:`Roles` — scoped role-authority context manager
- :func:`roles` — factory convenience for ``agent.roles()``
- :class:`RoleBindingError` — raised on missing role binding
- :class:`Authority` — multi-principal authority composer
- :class:`DependencyMode` — lazy vs eager evaluation mode enum
- :class:`Dependency` — single downstream dependency node
- :func:`lazy` — lazy dependency constructor
- :func:`eager` — eager dependency constructor
- :class:`ResolutionResult` — single dependency resolution outcome
- :class:`TopologyLog` — immutable topology snapshot
- :class:`DownstreamContext` — dependency + heritage + overrides manager
- :class:`AgentGraph` — lightweight DAG of interconnected contexts
- :class:`MissingDependencyError` — raised on unsatisfied dependency
"""

from .agent_engine import AgentEngine
from .agent_session import AgentSession
from .agent_status import AgentStatus
from .capability import (
    CapabilityMetadata,
    CapabilityRegistration,
    CapabilityType,
    infer,
    planner,
    playbook,
    router,
    tool,
)
from .dispatch import (
    CapabilityDispatcher,
    DispatchResult,
)
from .downstream import (
    AgentGraph,
    Dependency,
    DependencyMode,
    DownstreamContext,
    MissingDependencyError,
    ResolutionResult,
    TopologyLog,
    eager,
    lazy,
)
from .events import (
    Event,
    EventStream,
    EventType,
)
from .healing import (
    GuardConfig,
    Healer,
    HealingHook,
    HealingResult,
    HealingState,
    heal,
)
from .roles import (
    Authority,
    Principal,
    RoleBindingError,
    Roles,
    roles,
)
from .tasklist import (
    TaskList,
    TaskStep,
    TaskStepStatus,
)
from .traces import (
    ActivityKind,
    ExecutionTrace,
    GuardMetadata,
    InteractionTrace,
    TurnRole,
    WorkspaceActivity,
)

__all__ = [
    # Phase 1 — lifecycle
    "AgentStatus",
    "AgentSession",
    "AgentEngine",
    # Phase 2 — capabilities & dispatch
    "CapabilityType",
    "CapabilityMetadata",
    "CapabilityRegistration",
    "tool",
    "infer",
    "playbook",
    "planner",
    "router",
    "DispatchResult",
    "CapabilityDispatcher",
    # Phase 3 — observability
    "GuardMetadata",
    "TurnRole",
    "InteractionTrace",
    "ActivityKind",
    "WorkspaceActivity",
    "ExecutionTrace",
    "TaskStepStatus",
    "TaskStep",
    "TaskList",
    "EventType",
    "Event",
    "EventStream",
    # Phase 4 — auto-healing
    "GuardConfig",
    "HealingState",
    "HealingHook",
    "HealingResult",
    "Healer",
    "heal",
    # Phase 4 — roles
    "Principal",
    "Roles",
    "roles",
    "RoleBindingError",
    "Authority",
    # Phase 4 — downstream
    "DependencyMode",
    "Dependency",
    "lazy",
    "eager",
    "ResolutionResult",
    "TopologyLog",
    "DownstreamContext",
    "AgentGraph",
    "MissingDependencyError",
]
