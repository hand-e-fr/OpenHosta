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
]
