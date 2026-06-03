__version__ = "5.0.0"

from .core.audit import register_audit_callback, unregister_audit_callback
from .core.cost_tracker import track_costs
from .core.errors import UncertaintyError
from .core.logger import (
    conversation,
    markdown,
    print_last_decoding,
    print_last_probability_distribution,
    print_last_prompt,
    print_last_uncertainty,
    readable,
)
from .core.meta_prompt import MetaPrompt
from .core.uncertainty import safe
from .defaults import config, reload_dotenv
from .exec.ask import ask, ask_async, ask_stream, ask_stream_async
from .exec.closure import closure, closure_async
from .exec.emulate import emulate, emulate_async
from .exec.emulate_variants import emulate_variants
from .guarded.primitives import Guarded as GuardedPrimitive
from .guarded.wrapper import GuardMetadata, Guarded, guard_info, guarded_to_json, guarded_to_markdown, guarded_to_python
from .models import OpenAICompatibleModel
from .models import OpenAICompatibleModel as Model
from .pipelines import OneTurnConversationPipeline, Pipeline

# from .semantics import SemanticSet, SemanticDict # Maybe in 5.0
from .semantics.operators import test, test_async
from .utils.gather_data import gather_data, gather_data_async

DefaultModel = config.DefaultModel
DefaultPipeline = config.DefaultPipeline

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

# V5 - Guarded API publique
from openhosta.guarded.api import guard, unguard
from openhosta.guarded.primitives import GuardConfig as GuardedGuardConfig

__all__ = (
    "ask",
    "ask_async",
    "ask_stream",
    "ask_stream_async",
    "emulate",
    "emulate_async",
    "emulate_variants",
    "closure",
    "closure_async",
    "gather_data",
    "gather_data_async",
    "SemanticSet",
    "SemanticDict",
    "config",
    "reload_dotenv",
    "Model",
    "DefaultModel",
    "DefaultPipeline",
    "OpenAICompatibleModel",
    "MetaPrompt",
    "print_last_prompt",
    "print_last_decoding",
    "conversation",
    "readable",
    "markdown",
    "print_last_probability_distribution",
    "print_last_uncertainty",
    "Pipeline",
    "OneTurnConversationPipeline",
    "safe",
    "test",
    "test_async",
    "UncertaintyError",
    "track_costs",
    "Guarded",
    "register_audit_callback",
    "unregister_audit_callback",
    # V5 exports
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
    "guard",
    "unguard",
    "GuardedGuardConfig",
    "GuardMetadata",
    "guard_info",
    "guarded_to_python",
    "guarded_to_json",
    "guarded_to_markdown",
)
