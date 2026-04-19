# Meta-Prompt Improvement Suggestions

> Analysis of [meta_prompt.py](file:///home/ebatt/VSCode_GitRepos/OpenHosta.git/src/OpenHosta/core/meta_prompt.py) and the full push/pull pipeline.

---

## Current prompt (condensed)

```
You will act as a simulator for functions that cannot be implemented in actual code.
I'll provide you with function definitions described in Python syntax. …
Instead, imagine a realistic or reasonable output that matches the function description.

Here's the function definition:
{{ python_type_definition_dict }}

def {{ function_name }}({{ function_args }}) -> {{ function_return_type_name }}:
    """{{ function_doc }}"""
    ...behavior to be simulated...
    return ...appropriate return value...

OUTPUT FORMAT:
Respond with only the return value, placed inside a single fenced Python code block.
```

---

## Category 1 — Role Framing & Structural Clarity

### 1. Tighten the "simulator" identity

**Problem:** The current preamble says *"imagine a realistic or reasonable output"*. This gives the LLM permission to be creative rather than deterministic, which increases retry rates for factual functions.

**Suggestion:** Split the role instruction into two stances — *factual* vs *creative* — controlled by a template variable:

```jinja2
{% if factual_mode %}
You simulate a Python function. Your output MUST be factually accurate, verifiable data.
If you are unsure, use the most widely accepted answer. Do not invent facts.
{% else %}
You simulate a Python function. Your output should be realistic and plausible,
consistent with the function's docstring description.
{% endif %}
```

The `factual_mode` flag could be inferred automatically from the docstring (presence of keywords like "list", "capital of", "translate") or set via `force_template_data`.

**Impact:** Reduces hallucination on knowledge-retrieval tasks, cuts retry count.

---

### 2. Move the type definitions AFTER the function signature

**Problem:** Currently `{{ python_type_definition_dict }}` is rendered *before* the function signature. The LLM reads the type docs (e.g. a dataclass definition) without knowing which function they relate to. This hurts context grounding, especially with multiple nested types.

**Current order:**
```
type definitions  ← reader doesn't yet know why these matter
def my_func(…)
```

**Suggested order:**
```
def my_func(…) -> ReturnType:
    """docstring"""

# Type definitions used above:
{{ python_type_definition_dict }}
```

This mirrors how a developer reads code: signature first, then look up types.

**Impact:** Better type compliance, especially for nested dataclasses.

---

### 3. Add an explicit "contract" section

**Problem:** The system prompt mixes role, type docs, output format, and examples in a flat flow. LLMs (especially newer reasoning models) perform better with clearly delineated sections.

**Suggestion:**
```jinja2
## ROLE
You simulate Python functions...

## FUNCTION
```python
def {{ function_name }}({{ function_args }}) -> {{ function_return_type_name }}:
    """{{ function_doc }}"""
```

## TYPE DEFINITIONS
{{ python_type_definition_dict }}

## OUTPUT CONTRACT
{{ output_format_block }}

{% if examples_database %}
## EXAMPLES
{{ examples_database }}
{% endif %}
```

Using markdown headers gives reasoning models explicit section boundaries to attend to.

**Impact:** Cleaner attention patterns, easier to extend/override individual sections.

---

## Category 2 — Output Format Control

### 4. Type-specific output examples (biggest win)

**Problem:** The current `OUTPUT FORMAT` section gives a single generic example (`"your answer here"` for `str`). For complex types (dataclass, list[dataclass], dict, tuple), the LLM has to *guess* the expected serialization format. This is the #1 source of parse failures.

**Suggestion:** Generate a type-specific example automatically from the GuardedType. The `_type_py_repr` already contains a structural description; we just need to produce a *populated instance* example.

```python
# In analizer.py, new function:
def generate_output_example(p_type) -> str:
    """Generate a concrete example value for the return type."""
    guarded = TypeResolver.resolve(p_type)
    if hasattr(guarded, '_type_py') and is_dataclass(guarded._type_py):
        # Build a placeholder dict from field names
        fields = dataclasses.fields(guarded._type_py)
        example = {f.name: _example_for_type(f.type) for f in fields}
        return f"{guarded._type_py.__name__}({', '.join(f'{k}={v!r}' for k,v in example.items())})"
    ...
```

Then in the template:
```jinja2
Example for return type `{{ function_return_type_name }}`:
```python
{{ output_example }}
```
```

**Impact:** Dramatically reduces parse errors for structured types. The `pull_extract_data_section` code already handles both `ClassName(...)` and `{...}` formats, so either example works.

---

### 5. Explicitly forbid wrapping / preamble patterns

**Problem:** Many models add preamble text like *"Here is the result:"* or *"Based on the function..."* before the code block. The `pull_extract_data_section` strips trailing code blocks but chokes on *leading* prose when the code block isn't the last thing in the response.

**Suggestion:** Add an emphatic negative instruction:

```jinja2
## OUTPUT CONTRACT
Your entire response MUST be a single fenced Python code block. Nothing else.
Do NOT include any text, explanation, markdown headers, or commentary before or after the block.

CORRECT:
```python
42
```

WRONG:
Here is the result:
```python
42
```
```

Also consider adding a "canary" check: if `pull_extract_data_section` finds text before the *first* ````python`, it should log a warning and try to extract the *first* (not last) code block instead.

**Impact:** Reduces the "known gap" documented in [emulate_pipeline.md L274-276](file:///home/ebatt/VSCode_GitRepos/OpenHosta.git/docs/emulate_pipeline.md#L274-L276).

---

### 6. Unify constructor vs dict format for structured types

**Problem:** For dataclasses and Pydantic models, the LLM sometimes returns a constructor call (`Person(name="Alice", age=30)`) and sometimes returns a dict (`{"name": "Alice", "age": 30}`). Both are parseable, but dict is safer because `ast.literal_eval` can parse it directly without needing to handle `ast.Call` trees.

**Suggestion:** Explicitly tell the LLM which format to use:

```jinja2
{% if is_structured_return %}
Return the value as a Python dict literal (NOT a constructor call).
Example:
```python
{"name": "Alice", "age": 30}
```
{% endif %}
```

The `is_structured_return` flag can be set when `analyse.type` resolves to a dataclass, Pydantic model, or TypedDict.

**Impact:** Simplifies `_parse_heuristic` code paths and makes the pipeline more robust to model differences.

---

## Category 3 — Type Documentation Quality

### 7. Include field descriptions from docstrings / Pydantic `Field(description=...)`

**Problem:** The `python_type_definition_dict` for dataclasses only shows field names and types:

```python
@dataclass
class President:
    name: str
    start_date: str
    end_date: str
```

But for Pydantic models, the `describe()` function in `subclassablepydantic.py` already extracts rich field descriptions, aliases, required/optional markers, and examples. This discrepancy means the LLM gets less context for dataclasses than for Pydantic models.

**Suggestion:** Enrich `guarded_dataclass` repr to include:
- Field docstrings (from `__doc__` on the class, parsed per-field, or from `metadata`)
- Default values when present
- Type constraints (e.g. `int` with a known range)

```python
# Enhanced _type_py_repr for dataclasses:
@dataclass
class President:
    name: str           # Full name of the president
    start_date: str     # Format: YYYY-MM-DD
    end_date: str       # Format: YYYY-MM-DD, or "incumbent"
```

**Impact:** Better field-level accuracy, especially for date/format-sensitive fields.

---

### 8. Show enum values inline in function signature for simple enums

**Problem:** For enum return types, the enum definition appears in `python_type_definition_dict`, which is far from the function signature. The LLM sometimes "forgets" the allowed values.

**Suggestion:** For enums with ≤ 8 members, inline the values directly in the function signature:

```jinja2
def classify_sentiment(text: str) -> Sentiment:  # Sentiment ∈ {POSITIVE, NEGATIVE, NEUTRAL}
```

The full definition can still appear in the type definitions section for larger enums.

**Impact:** Higher enum compliance, fewer `_parse_heuristic` fallbacks.

---

### 9. Add `{{ parameter_constraints }}` for value-range hints

**Problem:** The user's docstring is the only source of parameter semantics. But often the *value* itself carries implicit constraints (e.g. a `year: int` parameter receiving `2024` implies the domain is years, not arbitrary integers). The LLM doesn't know this.

**Suggestion:** Add an optional `parameter_constraints` variable that can be auto-generated or manually injected:

```jinja2
{% if parameter_constraints %}
## PARAMETER CONSTRAINTS
{{ parameter_constraints }}
{% endif %}
```

Auto-generation heuristics:
- `int` value > 1900 and < 2100 → likely a year
- `str` value matching ISO date pattern → note "date in ISO format"
- `float` value between 0 and 1 → likely a probability or ratio

**Impact:** Better contextual grounding for the LLM's simulation.

---

## Summary — Priority Ranking

| # | Suggestion | Effort | Impact | Priority |
|---|---|---|---|---|
| 4 | Type-specific output examples | Medium | 🔴 High | **P0** |
| 5 | Forbid wrapping/preamble | Low | 🔴 High | **P0** |
| 2 | Type defs after signature | Low | 🟡 Medium | **P1** |
| 6 | Unify constructor vs dict format | Low | 🟡 Medium | **P1** |
| 3 | Explicit section headers | Low | 🟡 Medium | **P1** |
| 1 | Factual vs creative mode | Low | 🟡 Medium | **P2** |
| 7 | Field descriptions for dataclasses | Medium | 🟡 Medium | **P2** |
| 8 | Inline enum values | Low | 🟢 Low-Med | **P2** |
| 9 | Parameter constraints | Medium | 🟢 Low | **P3** |

> [!TIP]
> Items 4+5 alone would likely eliminate most of the parse failures and retries. They're also low-risk since the `pull` pipeline already handles the formats they'd produce.

> [!IMPORTANT]
> Any prompt change should be A/B tested against the existing functional test suite (`tests/typing/` and `tests/functionnal/`) to verify that it doesn't regress on models other than GPT-4o (e.g. local Ollama, DeepSeek).
