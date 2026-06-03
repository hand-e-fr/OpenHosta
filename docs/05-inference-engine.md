# Inference Engine — OpenHosta V5

## Principle

**Explicit is better than implicit.** A stub `@infer`/`@planner`/`@router`
cannot be called directly without a backend. Use one of these three patterns:

```python
# Pattern A: Inside an Agent (backend injected automatically)
agent.get("Hello")  # backend injected from agent's _backend

# Pattern B: Standalone with explicit backend
result = model.infer(my_stub, name="Alice")  # backend passed explicitly

# Pattern C: Decorator binding (canonical)
@model.infer(tags=["lang"])
def greet(name: str) -> str:
    """Salut poliment."""
    ...
result = greet(name="Alice")  # backend bound at decoration time
```

Calling the stub directly without a backend raises `NotImplementedError` with
a clear message pointing to the correct API.

## `@model.infer(tags=[...])` — Canonical Binding

The recommended pattern. Binds a stub to a specific backend at decoration time:

```python
from openhosta import BackendModel

model = BackendModel(
    provider="openai_compatible",
    model_name="Qwen3.6-27B-AWQ-INT4",
    base_url="http://127.0.0.1:8000/v1",
    api_key="none",
)

@model.infer(tags=["demo"])
def greet(name: str) -> str:
    """Salut poliment."""
    ...

# Backend bound at decoration time — no need to pass it explicitly
result = greet(name="Alice")
# → "Bonjour, Alice."
```

This decorator combines:
1. **Metadata registration** in `_default_registry` (for standalone usage).
2. **Inference delegation** bound to the specific `BackendModel`.

## `model.infer(func, *args, **kwargs)` — Direct Execution

For standalone decorated functions that registered with `@infer` (metadata only):

```python
from openhosta import BackendModel, infer

model = BackendModel(
    provider="openai_compatible",
    model_name="Qwen3.6-27B-AWQ-INT4",
    base_url="http://127.0.0.1:8000/v1",
    api_key="none",
)

@infer(tags=["demo"])
def greet(name: str) -> str:
    """Salut poliment."""
    ...

# Explicit backend passed at call time
result = model.infer(greet, name="Alice")
print(result)  # "Bonjour, Alice."
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `func` | A function decorated with `@infer`, `@planner`, or `@router` |
| `*args` | Positional arguments forwarded to the inference engine |
| `**kwargs` | Keyword arguments forwarded to the inference engine |

### Returns

The parsed result from the LLM backend (unwrapped from `Guarded[T]`).

### Errors

| Scenario | Exception |
|----------|-----------|
| Function not decorated | `ValueError` |
| Inference fails (backend unreachable) | `RuntimeError` |
| LLM response doesn't match return type | `RuntimeError` |
| `@model(tags=...)` misuse | `TypeError` (redirect to `@model.infer`) |

## `Agent.get()` — Per-Agent Inference

When called from an `Agent`, inference capabilities are executed with the
agent's backend automatically injected. The dispatcher routes to the capability
and passes `_backend=model` in kwargs:

```python
@model.compile()
class MyAgent(Agent):
    @model.infer(tags=["lang"])
    def translate(self, texte: str) -> str:
        """Translate text."""
        ...

agent = MyAgent()
agent.recruit()
result = agent.get("Traduis: Hello")  # backend injected automatically
agent.free()
```

## Test Examples

### 1. `@model.infer` — canonical binding

```python
@model.infer(tags=["demo"])
def greet(name: str) -> str:
    """Répond poliment à une personne."""
    ...

result = greet(name="Alice")
# → "Bonjour, Alice."
```

### 2. `@infer` + `model.infer()` — deferred backend

```python
@infer(tags=["nlp"])
def parse_sentiment(text: str) -> dict[str, float]:
    """Analyse le sentiment."""
    ...

result = model.infer(parse_sentiment, text="Je suis content")
# → {"positive": 0.85, "negative": 0.05, "neutral": 0.10}
```

### 3. Dataclass return

```python
from dataclasses import dataclass

@dataclass
class Summary:
    title: str
    bullet_points: list[str]

@model.infer(tags=["nlp"])
def summarize(text: str) -> Summary:
    """Résume le texte."""
    ...

result = summarize(text="Long article...")
# → Summary(title="...", bullet_points=[...])
```

### 4. Non-stub → direct execution

```python
@model.infer(tags=["demo"])
def fallback_infer(msg: str) -> str:
    """Inférence avec fallback."""
    return f"direct: {msg}"

result = fallback_infer("test")  # No LLM call, executes directly
# → "direct: test"
```

Non-stub functions are detected by `is_stub()` and bypass the inference engine.

### 5. Router stub → LLM classification

```python
@model.infer(tags=["dispatch"])
@router(priority=-10)
def intent_router(msg: str) -> str:
    """Classe l'intention et retourne 'route:greeting', 'route:query'."""
    ...

result = intent_router(msg="Quel temps fait-il ?")
# → "route:query"
```

### 6. Planner stub → goal decomposition

```python
@model.infer(tags=["planning"])
@planner()
def plan_steps(goal: str) -> list[str]:
    """Décompose un objectif en étapes exécutables."""
    ...

result = plan_steps(goal="Déployer en production")
# → ["1. Tests", "2. Staging", "3. Deploy"]
```

### 7. Backend unreachable

```python
bad_model = BackendModel(
    provider="openai_compatible",
    model_name="test",
    base_url="http://invalid-host:9999/v1",
    api_key="",
)

@bad_model.infer(tags=["demo"])
def greet(name: str) -> str:
    """Salut."""
    ...

try:
    greet(name="Alice")
except RuntimeError as e:
    print(e)  # "Inference failed for 'greet': Backend call failed: ..."
```

### 8. Parsing error (type mismatch)

```python
@model.infer(tags=["demo"])
def get_number(text: str) -> int:
    """Extrait un nombre entier du texte."""
    ...

# If LLM returns "environ quatre" instead of a number:
try:
    get_number(text="Il y a environ quatre chats")
except RuntimeError:
    pass  # parse_guarded failed to validate int
```

### 9. V5 convention — enriched prompt

```python
@model.infer(tags=["demo"])
def compute_correlation(x: list[float], y: list[float]) -> float:
    """Calcule le coefficient de corrélation de Pearson.

    Utilise la formule standard :
    r = Σ((xi - x̄)(yi - ȳ)) / √(Σ(xi - x̄)² × Σ(yi - ȳ)²)
    """
    ...

# The long_description enriches the prompt:
# **Signature:** `compute_correlation(x: list[float], y: list[float]) -> float`
#
# **Docstring:**
# Calcule le coefficient de corrélation de Pearson.
#
# Utilise la formule standard : ...
result = compute_correlation(x=[1.0, 2.0], y=[3.0, 4.0])
# → 1.0
```

### 10. Direct call without backend → NotImplementedError

```python
@infer(tags=["demo"])
def greet(name: str) -> str:
    """Salut poliment."""
    ...

greet("Alice")  # ❌ NotImplementedError
# → "This capability 'greet' is a stub and requires a backend.
#    Use model.infer(greet, ...) or Agent.get(...) to execute it."
```

### 11. `@model(tags=...)` misuse → TypeError

```python
model(tags=["demo"])(some_func)  # ❌ TypeError
# → "BackendModel is not a decorator. Use ``@model.infer(tags=[...])`` ..."
```

## Behind the Scenes

```
greet(name="Alice")  # via @model.infer(tags=[...])
  │
  ▼  wrapper created by @model.infer decorator
  │
  ▼  execute_inference(func, meta, model, name="Alice")
  │
  ▼  build_infer_prompt() → structured prompt
  │
  ▼  call_backend() → HTTP POST to LLM
  │
  ▼  parse_guarded() → Guarded[T] validation
  │
  ▼  return result
```

## Comparison: Three Execution Paths

| Aspect | `agent.get(msg)` | `model.infer(func, ...)` | `@model.infer(tags=...)` |
|--------|------------------|--------------------------|--------------------------|
| Context | Agent session | Standalone | Bound at decoration |
| Routing | Automatic (priority-based) | Explicit (you choose) | Direct call |
| Backend | Injected by Agent | Passed in model | Bound to decorator |
| Registry | Per-agent `_registry` | `_default_registry` | `_default_registry` + agent |
| Fallback | Engine echo | RuntimeError on failure | RuntimeError on failure |
| Use case | Conversational agent | Targeted inference | Virtual body / standalone |
