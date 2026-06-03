# Agent & Backend — OpenHosta V5

## Agent Lifecycle

`Agent` is the primary public class. Every agent follows a three-phase lifecycle:

```
CONFIGURED ── recruit() ──▶ RECRUITED ── free() / kill() ──▶ FREED / KILLED
```

| State       | Meaning                                            |
|-------------|----------------------------------------------------|
| `CONFIGURED`| Agent constructed; capabilities defined, not running. |
| `RECRUITED` | A session exists; `agent.get(msg)` is callable.    |
| `FREED`     | Session terminated cleanly.                        |
| `KILLED`    | Session terminated abruptly (no cleanup).           |

### Virtual Body Pattern

An agent's capabilities are defined as **class methods**. At `__init__`, the agent
scans its own class for methods decorated with `@tool`, `@infer`, `@router`,
`@planner`, or `@playbook`, binds them to `self`, and registers them in a
**per-agent isolated registry**. This guarantees that each agent instance owns
its own capability set.

```python
from openhosta import Agent, BackendModel, tool, router

model = BackendModel(
    provider="openai_compatible",
    model_name="Qwen3.6-27B-AWQ-INT4",
    base_url="http://127.0.0.1:8000/v1",
    api_key="none",
)

# @model.compile() attaches the backend to the class
@model.compile()
class AssistantAgent(Agent):
    """Agent with a virtual body of capabilities."""

    # LLM-powered translation — stub bound to the model
    @model.infer(tags=["lang"])
    def translate(self, texte: str) -> str:
        """Translate from French to English."""
        ...

    # Deterministic math tool
    @tool(tags=["math"])
    def add_numbers(self, chiffres: str) -> str:
        """Sum all numbers found in the message."""
        import re
        nums = re.findall(r"\d+", chiffres)
        return str(sum(int(n) for n in nums))

    # LLM-powered router — stub bound to the model
    @router(tags=["dispatch"], priority=-10)
    def decide_route(self, msg: str) -> str:
        """Route to 'route:lang' for translation or 'route:math' for calculation."""
        ...

agent = AssistantAgent()
agent.recruit()
result = agent.get("Combien font 12 + 30 ?")  # Router → route:math → add_numbers
agent.free()
```

## Per-Agent Registry

Each `Agent` instance builds its own `CapabilityRegistration` at construction
time. The registry is populated in two phases:

1. **Merge** global `_default_registry` capabilities (for standalone functions, tests).
2. **Bind & register** class methods with `_capability` metadata (the agent's virtual body).

This design guarantees **isolation** between agent instances and supports both
the virtual body pattern and standalone decorated functions.

## BackendModel

`BackendModel` describes a single LLM backend configuration. It is an immutable
`@dataclass(frozen=True)` with the following fields:

| Field       | Type   | Default | Description              |
|-------------|--------|---------|--------------------------|
| `provider`  | `str`  | —       | Provider identifier      |
| `model_name`| `str`  | —       | Model name               |
| `base_url`  | `str`  | —       | API endpoint URL         |
| `api_key`   | `str`  | `""`    | API key                  |
| `tags`      | `tuple`| `()`    | Optional metadata tags   |
| `priority`  | `int`  | `0`     | Selection priority       |

### `@backend.compile()`

Class decorator that attaches `_backend = backend` to the decorated agent class.

```python
@backend.compile()
class MyAgent(Agent):
    pass
```

### `@model.infer(tags=[...])` — Canonical Binding

Decorator factory that binds a stub method to the backend. Combines metadata
registration and inference delegation in a single decorator:

```python
@model.infer(tags=["lang"])
def translate(self, texte: str) -> str:
    """Translate text."""
    ...  # stub → bound to model for inference
```

### Direct `@model(...)` is Forbidden

Calling `BackendModel` as a decorator raises `TypeError` with a clear
redirection message:

```python
model(tags=["lang"])(some_func)  # ❌ TypeError
# Use @model.infer(tags=[...]) instead
```

## BackendSelector

When multiple backends are available, `BackendSelector` resolves the best one:

```python
from openhosta import BackendModel, BackendSelector

candidates = [
    BackendModel(provider="a", model_name="m1", base_url="http://a"),
    BackendModel(provider="b", model_name="m2", base_url="http://b", tags=("fast",)),
]
selector = BackendSelector(candidates)

agent = Agent(backend=selector)
```

By default, the first candidate is returned. When constraints specify tags:

```python
best = selector.resolve(constraints={"tags": ["fast"]})
```

the first candidate whose `tag_set` intersects the requested tags is returned.

## Agent Properties

| Property       | Return type                  | Description                          |
|----------------|------------------------------|--------------------------------------|
| `status`       | `str`                        | Current lifecycle state              |
| `workspace`    | `Workspace`                  | Filesystem access surface            |
| `learning`     | `bool`                       | Learning mode flag                   |
| `reincarn`     | `bool`                       | Reincarnation flag                   |
| `agent_session`| `AgentSession \| None`       | The active session                   |
| `agent_engine` | `AgentEngine \| None`        | The engine that created the session  |
| `notes`        | `list[str]`                  | Free-form notes list                 |
| `_registry`    | `CapabilityRegistration`     | Per-agent isolated capability registry |

## Error Handling

| Scenario                         | Exception         |
|----------------------------------|-------------------|
| `recruit()` when not `CONFIGURED`| `RuntimeError`    |
| `free()` when not `RECRUITED`    | `RuntimeError`    |
| `get()` when not `RECRUITED`     | `RuntimeError`    |
| `Workspace(root)` with bad path   | `ValueError`      |
| `@model(tags=...)` misuse        | `TypeError`       |
| Stub called without backend       | `NotImplementedError` |
