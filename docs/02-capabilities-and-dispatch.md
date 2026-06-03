# Capabilities & Dispatch — OpenHosta V5

## Overview

Capabilities are class methods decorated with one of five decorators. When an
`Agent` is instantiated, it scans its own class for methods with `_capability`
metadata, binds them to `self`, and registers them in a **per-agent isolated
registry**. Standalone decorated functions register to `_default_registry`.

## Dispatch Priority

When `agent.get(msg)` is called, the dispatcher traverses capabilities in
this strict priority order — the first successful result wins:

1. **@router** — routing decision
2. **@planner** — goal decomposition
3. **@playbook** — multi-step workflow
4. **@infer** — LLM-based inference
5. **@tool** — deterministic routine
6. **Fallback** — `AgentEngine.execute_step()` (echoes the message)

## Two Binding Patterns

### Pattern A: `@model.infer(tags=[...])` — Bind to a specific backend

Canonical pattern for binding a stub to a backend. Combines metadata registration
and inference delegation:

```python
model = BackendModel(provider="...", model_name="...", base_url="...")

@model.infer(tags=["lang"])
def translate(texte: str) -> str:
    """Translate from French to English."""
    ...  # stub → inference via `model`
```

### Pattern B: `@infer(tags=[...])` — Metadata only, deferred backend

Registers metadata in `_default_registry`. The backend is injected later
by `Agent.get()` or `model.infer(func, ...)`:

```python
@infer(tags=["lang"])
def translate(texte: str) -> str:
    """Translate from French to English."""
    ...  # stub → backend injected by Agent.get() or model.infer()
```

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

@tool(tags=["math"])
def add_numbers(chiffres: str) -> str:
    """Sum all numbers found in the message."""
    import re
    nums = re.findall(r"\d+", chiffres)
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

@playbook(tags=["workflow"])
def code_review(msg: str) -> str:
    """Code review workflow."""
    # Step 1: parse
    # Step 2: analyze
    # Step 3: report
    return "Review complete"
```

## @planner

Marks a goal-decomposition / planning capability.

```python
from openhosta import planner

@planner(tags=["planning"])
def plan_tasks(msg: str) -> str:
    """Decompose goals into tasks."""
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
@router(tags=["dispatch"], priority=-10)
def keyword_router(msg: str) -> str:
    """Routage par mots-clés."""
    if "fichier" in msg.lower():
        return "route:list"
    return "route:default"

# Stub: LLM-powered semantic routing
@router(tags=["dispatch"], priority=-10)
def semantic_router(msg: str) -> str:
    """Classe l'intention sémantiquement."""
    ...  # stub → LLM delegation via model.infer() or Agent.get()
```

Router return conventions:
- `"route:list"` → dispatch to capabilities tagged with `"list"`
- `"route:analyze"` → dispatch to capabilities tagged with `"analyze"`
- Any other string → returned as-is (no routing)

## Virtual Body Pattern

The recommended pattern is to define capabilities as class methods inside the
`Agent`. At construction, the agent binds these methods to `self` and registers
them in its private registry:

```python
@model.compile()
class MyAgent(Agent):
    @model.infer(tags=["lang"])
    def translate(self, texte: str) -> str:
        """Translate text."""
        ...

    @tool(tags=["math"])
    def add_numbers(self, chiffres: str) -> str:
        """Sum numbers."""
        import re
        return str(sum(int(n) for n in re.findall(r"\d+", chiffres)))
```

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

### Msg Bridging

When the dispatcher routes with `msg` kwarg but the target function declares a
different first parameter (e.g. `texte`, `chiffres`), the dispatcher
automatically aliases `msg` to that parameter name. This enables seamless
`agent.get(msg)` → `capability(texte=msg)` dispatch.

### Per-Agent Registry

The dispatcher accepts an optional `registry` parameter. When called from
`Agent.get()`, the agent passes its own `_registry`:

```python
dispatcher = CapabilityDispatcher(registry=self._registry)
```

When called standalone, it defaults to `_default_registry`.

## Test Isolation

Since capabilities register to `_default_registry`, tests must clear it:

```python
import pytest
from openhosta.agent import _default_registry

@pytest.fixture(autouse=True)
def _clean_registry():
    _default_registry.clear()
    yield
    _default_registry.clear()
```
