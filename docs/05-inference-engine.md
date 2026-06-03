# Inference Engine — OpenHosta V5

## Principle

**Explicit is better than implicit.** A stub `@infer`/`@planner`/`@router`
cannot be called directly without a backend. Use one of these two patterns:

```python
# Pattern A: Inside an Agent
agent.get("Hello")  # backend injected automatically

# Pattern B: Standalone, explicit backend
result = model.infer(my_stub, name="Alice")  # backend passed explicitly
```

Calling the stub directly without a backend raises `NotImplementedError` with
a clear message pointing to the correct API.

## model.infer()

`BackendModel.infer(func, *args, **kwargs)` executes inference for a decorated
function using this backend.

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

## Test Examples

### 1. Simple stub → successful inference

```python
@infer(tags=["demo"])
def greet(name: str) -> str:
    """Répond poliment à une personne."""
    ...

model.infer(greet, name="Alice")
# → "Bonjour, Alice."
```

### 2. Structured return (dict)

```python
@infer(tags=["nlp"])
def parse_sentiment(text: str) -> dict[str, float]:
    """Analyse le sentiment et retourne {positive, negative, neutral}."""
    ...

model.infer(parse_sentiment, text="Je suis content")
# → {"positive": 0.85, "negative": 0.05, "neutral": 0.10}
```

The response is validated by `parse_guarded()` which wraps it in `Guarded[dict]`.

### 3. Dataclass return

```python
from dataclasses import dataclass

@dataclass
class Summary:
    title: str
    bullet_points: list[str]

@infer(tags=["nlp"])
def summarize(text: str) -> Summary:
    """Résume le texte."""
    ...

model.infer(summarize, text="Long article...")
# → Summary(title="...", bullet_points=[...])
```

### 4. Non-stub → direct execution

```python
@infer(tags=["demo"])
def fallback_infer(msg: str) -> str:
    """Inférence avec fallback."""
    return f"direct: {msg}"

result = fallback_infer("test")  # No LLM call, executes directly
# → "direct: test"
```

Non-stub functions are detected by `is_stub()` and bypass the inference engine.

### 5. Router stub → LLM classification

```python
@router(tags=["demo"], priority=-10)
def intent_router(msg: str) -> str:
    """Classe l'intention et retourne 'route:greeting', 'route:query' ou 'route:unknown'."""
    ...

model.infer(intent_router, msg="Quel temps fait-il ?")
# → "route:query"
```

### 6. Planner stub → goal decomposition

```python
@planner(tags=["demo"])
def plan_steps(goal: str) -> list[str]:
    """Décompose un objectif en étapes exécutables."""
    ...

model.infer(plan_steps, goal="Déployer en production")
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

try:
    bad_model.infer(greet, name="Alice")
except RuntimeError as e:
    print(e)  # "Inference failed for 'greet': Backend call failed: ..."
```

### 8. Parsing error (type mismatch)

```python
@infer(tags=["demo"])
def get_number(text: str) -> int:
    """Extrait un nombre entier du texte."""
    ...

# If LLM returns "environ quatre" instead of a number:
try:
    model.infer(get_number, text="Il y a environ quatre chats")
except RuntimeError:
    pass  # parse_guarded failed to validate int
```

### 9. V5 convention — enriched prompt

```python
@infer(tags=["demo"])
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
result = model.infer(compute_correlation, x=[1.0, 2.0], y=[3.0, 4.0])
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

### 11. Non-decorated function → ValueError

```python
def not_decorated(x: int) -> int:
    return x * 2

model.infer(not_decorated, x=5)  # ❌ ValueError
# → "Function 'not_decorated' is not a registered capability.
#    Decorate it with @infer, @planner, or @router first."
```

## Behind the Scenes

```
model.infer(greet, name="Alice")
  │
  ▼  validates _capability metadata exists
  │
  ▼  execute_inference(func, meta, backend, ...)
  │
  ▼  build_infer_prompt() → structured prompt
  │
  ▼  call_backend() → HTTP POST to LLM
  │
  ▼  parse_guarded() → Guarded[T] validation
  │
  ▼  unguard() → unwrap value
  │
  ▼  return result
```

## Comparison: Agent vs model.infer()

| Aspect | `agent.get(msg)` | `model.infer(func, ...)` |
|--------|------------------|--------------------------|
| Context | Agent session | Standalone |
| Routing | Automatic (priority-based) | Explicit (you choose the function) |
| Backend | Injected by Agent | Passed in the model |
| Dispatch | Router → Planner → Playbook → Infer → Tool | Direct call to the stub |
| Fallback | Engine echo | RuntimeError on failure |
| Use case | Conversational agent | Targeted inference |
