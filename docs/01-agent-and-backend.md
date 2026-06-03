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

### Example

```python
from openhosta import Agent, BackendModel

backend = BackendModel(
    provider="openai_compatible",
    model_name="cyankiwi/Qwen3.6-27B-AWQ-INT4",
    base_url="http://127.0.0.1:8000/v1",
    api_key="none",
)

@backend.compile()
class MyAgent(Agent):
    pass

agent = MyAgent()
agent.recruit(quota=4096)  # CONFIGURED → RECRUITED
result = agent.get("Hello")
agent.free()               # RECRUITED → FREED
```

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

`backend.compile()` returns a class decorator that attaches `_backend = backend`
to the decorated class. When `Agent.__init__()` runs, it reads `_backend` from
the class to instantiate the correct `AgentEngine`.

```python
@backend.compile()
class MyAgent(Agent):
    pass
```

The constructor may override the class-level backend:

```python
agent = MyAgent(backend=another_backend)  # instance-level override
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

## Error Handling

| Scenario                         | Exception         |
|----------------------------------|-------------------|
| `recruit()` when not `CONFIGURED`| `RuntimeError`    |
| `free()` when not `RECRUITED`    | `RuntimeError`    |
| `get()` when not `RECRUITED`     | `RuntimeError`    |
| `Workspace(root)` with bad path   | `ValueError`      |
