# Capabilities & Dispatch — OpenHosta V5

## Overview

Capabilities are Python callables decorated with one of five decorators.
Each decorated function is automatically registered in the global
`CapabilityRegistration` singleton and executed by `CapabilityDispatcher`.

## Dispatch Priority

When `agent.get(msg)` is called, the dispatcher traverses capabilities in
this strict priority order — the first successful result wins:

1. **@router** — routing decision
2. **@planner** — goal decomposition
3. **@playbook** — multi-step workflow
4. **@infer** — LLM-based inference
5. **@tool** — deterministic routine
6. **Fallback** — `AgentEngine.execute_step()` (echoes the message)

## Decorator API

All five decorators share the same signature:

```python
@decorator(
    name: str,
    description: str = "",
    tags: list[str] | tuple[str, ...] | None = None,
    priority: int = 0,
    requires_async: bool = False,
)
def my_capability(msg: str) -> str:
    ...
```

| Parameter        | Description                                  |
|------------------|----------------------------------------------|
| `name`           | Unique identifier (dot-notation preferred)  |
| `description`    | Human-readable one-liner                     |
| `tags`           | Arbitrary search tags                        |
| `priority`       | Scheduling priority (lower = more urgent)    |
| `requires_async` | Whether the callable is async                |

---

## @tool

Marks a deterministic, side-effect-capable routine.

```python
from openhosta import tool

@tool(name="math.add", description="Add two numbers from a message")
def add_tool(msg: str) -> str:
    import re
    nums = re.findall(r"\d+", msg)
    return str(sum(int(n) for n in nums))
```

## @infer

Marks an LLM-based probabilistic capability.

```python
from openhosta import infer

@infer(name="nlp.summarize", description="Summarize text")
def summarize(msg: str) -> str:
    return f"Summary: {msg[:100]}..."
```

## @playbook

Marks a multi-step orchestrated workflow.

```python
from openhosta import playbook

@playbook(name="workflow.review", description="Code review workflow")
def code_review(msg: str) -> str:
    # Step 1: parse
    # Step 2: analyze
    # Step 3: report
    return "Review complete"
```

## @planner

Marks a goal-decomposition / planning capability.

```python
from openhosta import planner

@planner(name="plan.tasks", description="Decompose goals into tasks")
def plan_tasks(msg: str) -> str:
    return "1. First task\n2. Second task"
```

## @router

Marks a routing-decision capability.

```python
from openhosta import router

@router(name="route.intent", description="Route by user intent")
def route_by_intent(msg: str) -> str:
    if "search" in msg.lower():
        return "route: search_handler"
    return "route: default"
```

## CapabilityMetadata

Every registered capability carries a frozen `CapabilityMetadata`:

```python
@dataclass(frozen=True)
class CapabilityMetadata:
    name: str
    capacity_type: CapabilityType
    description: str = ""
    tags: tuple[str, ...] = ()
    priority: int = 0
    requires_async: bool = False
```

## CapabilityDispatcher

The dispatcher provides three routing strategies:

```python
from openhosta import CapabilityDispatcher

disp = CapabilityDispatcher()

# 1. Dispatch by name
result = disp.dispatch("math.add", msg="add 12 and 15")

# 2. Route by type
results = disp.route_by_type(CapabilityType.TOOL, msg="hello")

# 3. Route by tag
results = disp.route_by_tag("math", msg="hello")
```

Each strategy returns `DispatchResult(success, result, error, metadata)`.

## Test Isolation

Because `CapabilityRegistration` is a singleton, tests must clear the registry:

```python
import pytest
from openhosta import CapabilityRegistration

@pytest.fixture(autouse=True)
def _clean_registry():
    reg = CapabilityRegistration()
    reg.clear()
    yield
    reg.clear()
```
