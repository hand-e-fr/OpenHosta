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
from .events import (
    Event,
    EventStream,
    EventType,
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
]
