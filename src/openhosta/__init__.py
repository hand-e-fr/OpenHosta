__version__ = "5.0.0-dev"

# V5 - Backend
from .backend import BackendModel, BackendSelector
from .workspace import Workspace

# V5 - Guarded API
from .guarded.api import guard, unguard
from .guarded.defaults import ALLOW_CODE_EXECUTION
from .guarded.primitives import GuardConfig as GuardedGuardConfig
from .guarded.wrapper import GuardMetadata, Guarded, guard_info, guarded_to_json, guarded_to_markdown, guarded_to_python

# V5 - Agent runtime
from openhosta.agent import (
    AgentEngine,
    AgentSession,
    AgentStatus,
    Authority,
    CapabilityDispatcher,
    CapabilityRegistration,
    Event,
    EventStream,
    EventType,
    GuardConfig,
    Healer,
    Principal,
    Roles,
    TaskList,
    TaskStep,
    heal,
    infer,
    planner,
    playbook,
    router,
    tool,
)

__all__ = (
    # Backend
    "BackendModel",
    "BackendSelector",
    "Workspace",
    # Guarded API
    "guard",
    "unguard",
    "ALLOW_CODE_EXECUTION",
    "GuardedGuardConfig",
    "GuardMetadata",
    "Guarded",
    "guard_info",
    "guarded_to_json",
    "guarded_to_markdown",
    "guarded_to_python",
    # Agent runtime
    "AgentEngine",
    "AgentSession",
    "AgentStatus",
    "tool",
    "infer",
    "playbook",
    "planner",
    "router",
    "CapabilityRegistration",
    "CapabilityDispatcher",
    "Event",
    "EventStream",
    "EventType",
    "TaskList",
    "TaskStep",
    "Healer",
    "heal",
    "GuardConfig",
    "Principal",
    "Roles",
    "Authority",
)
