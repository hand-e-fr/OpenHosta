# 🛠️ Debugging and Inspection

OpenHosta provides powerful tools to inspect how your LLM functions behave and to verify the quality of the generated data.

## I. Using Guarded Types for Introspection

By default, `emulate()` returns native Python types (int, str, list, etc.). While convenient, these types lose the "provenance" metadata (the prompt that produced them, the raw LLM response, etc.).

To keep this metadata, use the `Guarded` wrapper or a specific `Guarded` type in your annotation:

```python
from OpenHosta import emulate, Guarded

# Native return (no metadata)
def get_age(name: str) -> int:
    return emulate()

# Guarded return (metadata preserved)
def get_age_guarded(name: str) -> Guarded[int]:
    return emulate()
```

### Why use Guarded types?
1.  **Traceability**: You can see the exact conversation that produced the value.
2.  **Uncertainty**: You can check if the LLM was "confident" about the result.
3.  **Stability**: You can get a "clean" version of the data without LLM artifacts.

---

## II. Inspection Functions

Once you have a Guarded value, you can use the following functions:

### 1. `conversation(value)`
Prints the full conversation (System prompt + User prompt) that led to this value.

```python
age = get_age_guarded("John")
conversation(age)
```

### 2. `readable(value)`
Returns a human-friendly string representation of the value.
- It removes LLM artifacts (comments, extra text).
- It pretty-prints complex structures (lists, dicts).
- It is **stable**: `GuardedType(readable(val))` is guaranteed to produce the same value as the original.

### 3. `markdown(value)`
Same as `readable()`, but wrapped in Markdown code blocks for better rendering in reports or other LLMs.

---

## III. Comparison Table

| Feature | `str(val)` | `repr(val)` | `readable(val)` | `markdown(val)` |
| :--- | :--- | :--- | :--- | :--- |
| **Target** | Programmatic | Developers | Humans / Logs | Reports / LLMs |
| **Quotes** | No (for str) | Yes (for str) | No | Block if complex |
| **Format** | Default Python | Technical | Pretty-printed | Markdown Block |
| **Stability** | Yes | Yes | **Guaranteed** | Yes |

---

## IV. Debugging Workflows

### Inspecting a Function (Standard)
If you don't want to change your return types, you can always inspect the *function* itself to see its *last* execution:

```python
from OpenHosta import print_last_prompt

age = get_age("John")
print_last_prompt(get_age)
```

### Inspecting a Value (Recommended for Loops/Batch)
If you are calling a function many times, `print_last_prompt(func)` only shows the last one. Using `Guarded` types allows you to inspect *any* result at any time:

```python
results = [get_age_guarded(n) for n in names]

# Later, inspect a specific result
conversation(results[5])
print(f"Readable value: {readable(results[5])}")
```
