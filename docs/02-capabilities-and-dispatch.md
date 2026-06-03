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
    name: str | None = None,
    description: str | None = None,
    tags: list[str] | tuple[str, ...] | None = None,
    priority: int = 0,
    requires_async: bool = False,
)
def my_capability(msg: str) -> str:
    """Short description derived automatically."""
    ...
```

### V5 Convention — Automatic Derivation

| Parameter        | When not provided          | Source                           |
|------------------|----------------------------|----------------------------------|
| `name`           | `func.__name__`            | Function name                    |
| `description`    | First line of docstring    | `func.__doc__`                   |
| `long_description` | Signature + full docstring | Auto-generated for inference     |

```python
# Before (redundant)
@tool(name="list_files", description="Liste les fichiers", tags=["files"])
def list_files(msg: str) -> str:
    """Liste les fichiers."""
    return "files"

# V5 convention (derived)
@tool(tags=["files"])
def list_files(msg: str) -> str:
    """Liste les fichiers du workspace."""
    return "files"
# → name="list_files", description="Liste les fichiers du workspace."
# → long_description="**Signature:** `list_files(msg: str) -> str`\n**Docstring:**\nListe les fichiers..."
```

| Parameter        | Description                                  |
|------------------|----------------------------------------------|
| `name`           | Unique identifier (auto-derived from `__name__`) |
| `description`    | Human-readable one-liner (auto-derived from docstring) |
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

Marks an LLM-based probabilistic capability. When the decorated function is a
**stub** (body is only `...`), invocation delegates to the InferenceEngine.
Non-stub functions execute directly.

**Explicit is better than implicit**: a stub must be executed via
`model.infer()` or `Agent.get()`, not called directly.

```python
from openhosta import infer, BackendModel

@infer(tags=["nlp"])
def summarize(text: str) -> str:
    """Résume le texte fourni."""
    ...  # stub → LLM delegation

# ✅ Standalone: explicit backend
model = BackendModel(provider="...", model_name="...", base_url="...")
result = model.infer(summarize, text="Long article...")

# ✅ Via Agent: backend injected automatically
agent = Agent(backend=model)
agent.recruit()
result = agent.get("Résume ce texte")

# ❌ Direct call: raises NotImplementedError
# summarize("test")
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

Marks a routing-decision capability. When the decorated function is a **stub**,
invocation delegates to the InferenceEngine for LLM-powered classification.

The router's return value is interpreted by `Agent.get()`: if it starts with
`"route:"`, the dispatcher routes to capabilities tagged with the specified
target tag.

```python
from openhosta import router

# Non-stub: keyword-based routing (executes directly)
@router(tags=["demo"], priority=-10)
def keyword_router(msg: str) -> str:
    """Routage par mots-clés."""
    if "fichier" in msg.lower():
        return "route:list"
    return "route:default"

# Stub: LLM-powered semantic routing
@router(tags=["demo"], priority=-10)
def semantic_router(msg: str) -> str:
    """Classe l'intention sémantiquement."""
    ...  # stub → LLM delegation via model.infer() or Agent.get()
```

Router return conventions:
- `"route:list"` → dispatch to capabilities tagged with `"list"`
- `"route:analyze"` → dispatch to capabilities tagged with `"analyze"`
- Any other string → returned as-is (no routing)

## CapabilityMetadata

Every registered capability carries a frozen `CapabilityMetadata`:

```python
@dataclass(frozen=True)
class CapabilityMetadata:
    name: str
    capacity_type: CapabilityType
    description: str = ""            # Short (first line of docstring)
    long_description: str = ""       # Signature + full docstring
    tags: tuple[str, ...] = ()
    priority: int = 0
    requires_async: bool = False
```

`long_description` is automatically generated from the function's signature
and complete docstring. It is used by the InferenceEngine to build richer
prompts for LLM-backed stubs.

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
