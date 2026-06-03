# OpenHosta — V5

**Semantic layer for Python. Write what you mean. Guard types. Deploy agents.**

---

OpenHosta V5 introduces two core primitives: **Guarded Types** — first-class Python types with built-in validation, uncertainty tracking, and tolerance — and an **Agent Runtime** — a capability-driven engine for building, orchestrating, and deploying AI agents with roles, healing, streaming, and audit trails.

## Installation

OpenHosta V5 is currently a prototype under active development.

```sh
pip install git+https://github.com/hand-e-fr/OpenHosta.git@dev_version_5
```

Or clone and install locally:

```sh
git clone https://github.com/hand-e-fr/OpenHosta.git
cd OpenHosta
git checkout dev_version_5
pip install -e ".[tests]"
```

## Guarded Types

Guarded types wrap Python values with automatic validation, tolerance-aware comparisons, and metadata tracking. Every value can be queried for its confidence level, origin, and validation history.

```python
from openhosta import guard, unguard

# Guard a value — validate and wrap with metadata
result = guard("42", int)
# result: GuardedInt with value=42, confidence=1.0

# Access the raw value
raw = unguard(result)
# raw: 42

# Guarded types support collections, enums, unions, dataclasses, callables…
from openhosta.guarded import GuardedList, GuardedDict, GuardedEnum, GuardedUnion

items = GuardedList[str]([a, b, c])
mapping = GuardedDict[str, int]({x: 1, y: 2})
```

### Coverage

The guarded types module implements the full specification CR-01 through CR-09:

| Criterion | Description |
|-----------|-------------|
| CR-01 | Scalar guarded types (int, float, str, bytes, complex, bool, None, any) |
| CR-02 | Collection guarded types (list, dict, set, tuple) |
| CR-03 | Enum and literal guarded types |
| CR-04 | Union guarded types with automatic dispatch |
| CR-05 | Callable guarded types with signature validation |
| CR-06 | Dataclass guarded types with field-level guards |
| CR-07 | Tolerance-aware comparisons and uncertainty levels |
| CR-08 | Type resolution and metadata extraction |
| CR-09 | Proxy wrappers and transparent value access |

## Agent Runtime — Hello World V5

The agent runtime provides a capability-driven architecture for building, orchestrating, and deploying AI agents. The DX centers around three primitives: `Agent`, `BackendModel`, and `@compile()`.

### Hello World

```python
from openhosta import Agent, BackendModel, tool

# 1. Define your backend
backend = BackendModel(
    provider="openai_compatible",
    model_name="cyankiwi/Qwen3.6-27B-AWQ-INT4",
    base_url="http://127.0.0.1:8000/v1",
    api_key="none",
)

# 2. Declare your agent class and compile it against the backend
@backend.compile()
class MyAgent(Agent):
    """A minimal agent with one tool capability."""
    pass

# 3. Register a capability
@tool(name="math.add", description="Add two numbers from a message")
def add_tool(msg: str) -> str:
    import re
    nums = re.findall(r"\d+", msg)
    return str(sum(int(n) for n in nums))

# 4. Lifecycle: recruit -> interact -> free
agent = MyAgent()
agent.recruit(quota=4096)         # CONFIGURED → RECRUITED
result = agent.get("Add 12 and 15")  # Dispatches to @tool (returns "27")
print(result)                     # 27
agent.free()                      # RECRUITED → FREED
```

### Capability Decorators

| Decorator | Purpose |
|-----------|---------|
| `@tool`   | Deterministic routine |
| `@infer`  | LLM-based inference |
| `@playbook` | Multi-step workflow |
| `@planner` | Goal decomposition |
| `@router` | Routing decision |

### Agent Lifecycle

```
CONFIGURED ── recruit() ──▶ RECRUITED ── free() ──▶ FREED
                                   │
                              ── kill() ──▶ KILLED
```

### Key Classes

| Class | Description |
|-------|-------------|
| `Agent` | Héritable agent with lifecycle management |
| `BackendModel` | LLM backend configuration (`provider`, `model_name`, `base_url`) |
| `BackendSelector` | Multi-backend resolver with tag-based selection |
| `Workspace` | Governed filesystem access with path confinement |
| `CapabilityDispatcher` | Routes messages to registered capabilities |
| `CapabilityRegistration` | Global singleton registry for all capabilities |

### Full Feature Set

| Feature | Description |
|---------|-------------|
| **Capabilities** | First-class registration of tools, routers, planners, playbooks, and inferrers |
| **Roles & Authority** | Principal-based access control with role hierarchies |
| **Healing** | Automatic recovery hooks when a capability fails or returns invalid data |
| **Streaming** | Real-time event streams for task progress, intermediate results, and diagnostics |
| **Traces** | Full execution traces: interactions, workspace activity, and guard metadata per turn |
| **Task Lists** | Structured step-by-step task planning with per-step status tracking |
| **Downstream** | Dependency graphs for agent-to-agent communication and result passing |
| **Session API** | Isolated agent sessions with their own capability registries and state |

## Architecture

```
openhosta/
├── guarded/          # Guarded types — CR-01 to CR-09
│   ├── api/          # guard(), unguard() entry points
│   ├── primitives/   # GuardConfig, GuardedPrimitive, UncertaintyLevel
│   ├── scalars/      # GuardedInt, GuardedFloat, GuardedUtf8, …
│   ├── collections/  # GuardedList, GuardedDict, GuardedSet, GuardedTuple
│   ├── classes/      # GuardedEnum, guarded_dataclass
│   ├── literals/     # GuardedLiteral, guarded_literal
│   ├── unions/       # GuardedUnion, guarded_union
│   ├── callables/    # GuardedCallable
│   ├── resolver/     # Type resolution and metadata extraction
│   └── wrapper/      # Transparent proxy wrappers
└── agent/            # Agent runtime
    ├── engine/       # AgentEngine — main orchestrator
    ├── session/      # AgentSession — isolated execution context
    ├── capability/   # Capability registration and metadata
    ├── dispatch/     # CapabilityDispatcher — routing and execution
    ├── roles/        # Principal, Roles, Authority
    ├── healing/      # Healer, HealingHook, automatic recovery
    ├── events/       # EventStream, EventType — real-time streaming
    ├── traces/       # ExecutionTrace, InteractionTrace, WorkspaceActivity
    ├── tasklist/     # TaskList, TaskStep, step-level status
    ├── downstream/   # AgentGraph, dependency management
    └── status/       # AgentStatus — lifecycle states
```

## Contributing

We warmly welcome contributions. Browse existing issues to find contribution ideas.

## License

MIT License — see [LICENSE](LICENSE) for details.

## Authors

- **Emmanuel Batt** — Manager and Coordinator, Founder of Hand-e
- **William Jolivet** — DevOps, SysAdmin
- **Léandre Ramos** — AI Developer
- **Merlin Devillard** — UX Designer, Product Owner
