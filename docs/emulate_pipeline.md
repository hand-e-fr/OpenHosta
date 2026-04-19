# `emulate()` — Pipeline Reference

> **Purpose of this document**: Enable a future AI session to quickly understand how `emulate()` converts a Python function into an LLM call and back, without having to re-read all source files.
>
> Last updated: 2026-04-19. Covers the `streaming / generator` extension added in this session.

---

## 0. Entry Points

| Function | File | Mode |
|---|---|---|
| `emulate()` | `exec/emulate.py` | Sync, single value |
| `emulate_async()` | `exec/emulate.py` | Async, single value |
| `emulate()` (generator caller) | `exec/emulate.py` | Sync generator — `yield emulate()` |
| `emulate_async()` (async-generator caller) | `exec/emulate.py` | Async generator — `yield emulate_async()` |

`ask()` / `ask_async()` follow a simpler flow (no introspection) and are not covered here.

---

## 1. Stack Inspection — `get_caller_frame` + `get_hosta_inspection`

**Files**: `core/inspection.py`

```
emulate()
  └─ get_caller_frame()         # sys._getframe(2) → frame of the user function
  └─ get_hosta_inspection(frame)
        ├─ identify_function_of_frame(frame)
        │     walks parent frames / locals / globals to find the function pointer
        │     whose __code__ matches the frame's f_code
        └─ hosta_analyze(frame, function_pointer)  →  AnalyzedFunction
```

**Key object: `Inspection`** (stored as `function_pointer.hosta_inspection`)

```python
class Inspection:
    function_pointer   # the callable (used to cache hosta_inspection on it)
    frame              # last call frame
    analyse            # AnalyzedFunction (see below)
    logs               # dict — filled during pull phase
    force_llm_args     # dict — merged from inspection + call-site
    model              # Model instance chosen by pipeline
    pipeline           # Pipeline instance
```

**Key object: `AnalyzedFunction`**

```python
@dataclass
class AnalyzedFunction:
    name: str                       # function.__name__
    args: List[AnalyzedArgument]    # one per parameter, with value from the call frame
    type: Any                       # return type annotation (resolved, not a string)
    doc: str                        # __doc__
```

### Caller-context detection (generator mode — new)

**File**: `core/caller_context.py` [NEW]

```python
@dataclass
class CallerContext:
    is_async: bool      # CO_COROUTINE | CO_ASYNC_GENERATOR flag set
    is_generator: bool  # CO_GENERATOR | CO_ASYNC_GENERATOR flag set
    item_type: Any      # inner T from Iterator[T] / AsyncIterator[T] / Generator[T,...]
```

`detect_caller_context(frame)` reads `frame.f_code.co_flags` and unwraps the return annotation through `identify_function_of_frame` + `hosta_analyze`.

---

## 2. PUSH phase — Python → LLM messages

**File**: `pipelines/simple_pipeline.py` — `OneTurnConversationPipeline.push()`

```
push(inspection)
  ├─ push_detect_missing_types     fills in str/Any if annotation missing
  ├─ push_choose_model             selects Model from model_list by ModelCapabilities
  ├─ push_check_uncertainty        (only if inside safe() context) injects seed/logprobs
  ├─ push_select_meta_prompts      picks EMULATE_META_PROMPT + USER_CALL_META_PROMPT
  ├─ push_encode_inspected_data    calls encode_function() → dict of template variables
  └─ push_build_messages           renders Jinja2 templates → list[{role, content}]
```

### 2a. Template variables produced by `encode_function()`

**File**: `core/analizer.py`

| Variable | Source |
|---|---|
| `function_name` | `analyse.name` |
| `function_doc` | `analyse.doc` |
| `function_args` | `name: TypeName` inline string |
| `function_call_arguments` | `name = value` inline string |
| `variables_initialization` | long values placed outside the call |
| `function_return_type` | raw type object |
| `function_return_type_name` | `nice_type_name(analyse.type)` |
| `function_return_as_python_type` | `describe_type_as_python(analyse.type)` — calls `TypeResolver.resolve()` then `str()` on the GuardedType |
| `python_type_definition_dict` | for each arg and return type: fenced `python` block with the GuardedType string repr |

**Additional variables injected via `force_template_data`** (set as attribute on the function pointer, merged in `push_encode_inspected_data`):

```python
inspection.function_pointer.force_template_data = {"key": value}
```

**Variables only present when `push_streaming()` is called** (generator mode — new):

| Variable | Value |
|---|---|
| `is_streaming_generator` | `True` |
| `item_type_name` | `nice_type_name(ctx.item_type)` |

### 2b. Type description via `TypeResolver` + GuardedTypes

**File**: `guarded/resolver.py`

`TypeResolver.resolve(annotation)` recursively converts any Python annotation into a `GuardedPrimitive` subclass:

```
int          → GuardedInt
str          → GuardedUtf8
bool         → GuardedBool  (ProxyWrapper)
list[str]    → GuardedList[GuardedUtf8]
dict[str,int]→ GuardedDict[GuardedUtf8, GuardedInt]
MyDataclass  → guarded_dataclass(MyDataclass)  (dynamic subclass)
MyEnum       → guarded_enum(MyEnum)
Callable[..]→ GuardedCode  (returns a code block string)
Iterator[T]  → NOT resolved by TypeResolver — stripped to T first by CallerContext
```

The `__repr__` of the resulting GuardedType class becomes the `python_type_definition_dict` block in the prompt.

### 2c. Meta-prompts (Jinja2)

**File**: `core/meta_prompt.py`

Two templates are rendered and combined into `messages`:

**`EMULATE_META_PROMPT`** (system prompt):
```
You will act as a simulator...
[optional: {% if use_json_mode %}...{% endif %}]
[optional: {% if return_none_allowed %}...{% endif %}]
[optional: {% if allow_thinking %}...{% endif %}]
[optional: {% if is_streaming_generator %}...{% endif %}]   ← NEW

def {{ function_name }}({{ function_args }}) -> {{ function_return_type_name }}:
    """{{ function_doc }}"""
    return ...

{{ python_type_definition_dict }}
{{ function_return_as_python_type }}
[optional: {{ examples_database }}]
[optional: {{ chain_of_thought }}]
```

**`USER_CALL_META_PROMPT`** (user turn):
```
{{ variables_initialization }}
{{ function_name }}({{ function_call_arguments }})
```

> [!IMPORTANT]
> The following template variables exist in `EMULATE_META_PROMPT` but are **NOT populated by `encode_function()`** by default — they evaluate to Jinja2 `Undefined` (falsy) unless explicitly injected:
> `use_json_mode`, `allow_thinking`, `return_none_allowed`, `examples_database`, `chain_of_thought`, `is_streaming_generator`
>
> To activate them, either set them via `force_template_data` on the function pointer, or override `push_encode_inspected_data` in a custom Pipeline subclass.

### 2d. Generator mode: `push_streaming()` (new)

When `ctx.is_generator`, `emulate()` calls `pipeline.push_streaming()` instead of `pipeline.push()`. This method calls the standard `push()` chain but merges extra keys into `encoded_data` before rendering:

```python
encoded_data |= {
    "is_streaming_generator": True,
    "item_type_name": nice_type_name(ctx.item_type),
}
```

The `EMULATE_META_PROMPT` then renders the instruction block telling the LLM to output **one `\`\`\`python` block per item**, not a JSON array or a single block:

```
IMPORTANT: You must output each item of the sequence SEPARATELY.
Wrap each individual item in its own fenced Python code block, one per item:

\`\`\`python
item_1_value
\`\`\`

\`\`\`python
item_2_value
\`\`\`

Each block contains exactly one value of type {{ item_type_name }}.
```

---

## 3. LLM API call

**File**: `core/base_model.py` — `Model`

```python
# Standard (blocking)
response_dict = model.api_call(messages, llm_args)
    → model.generate(messages, **llm_args)
    → model._retry_wrapper(model._generate_without_retry, ...)

# Async
response_dict = await model.api_call_async(messages, llm_args)
    → loop.run_in_executor(executor, lambda: model.generate(...))

# Streaming (new, OpenAICompatibleModel only)
for chunk in model.generate_stream(messages, **llm_args):
    ...  # chunk: str delta
```

**`ModelCapabilities`** (used by `push_choose_model` to route to the right model):

```python
TEXT2TEXT   IMAGE2TEXT   JSON_OUTPUT   LOGPROBS   THINK   STREAMING (new)
```

---

## 4. PULL phase — LLM response → Python object

**File**: `pipelines/simple_pipeline.py` — `OneTurnConversationPipeline.pull()`

```
pull(inspection, response_dict)
  ├─ pull_extract_messages        → raw_response: str
  │     model.get_response_content(response_dict)
  │     catches reasoning field if present
  ├─ pull_extract_data_section    → response_string: str
  │     strips <think>…</think> tags (for reasoning models)
  │     strips surrounding quotes and ``` code blocks (last block)
  ├─ pull_type_data_section       → response_data: Any
  │     type_returned_data(response_string, inspection.analyse.type)
  │       → TypeResolver.resolve(expected_type) → GuardedType
  │       → GuardedType.attempt(response_string) → CastingResult
  │       → .unwrap() if not an explicitly Guarded annotation
  └─ pull_check_uncertainty       (only inside safe() context)
```

### 4a. `type_returned_data` + GuardedType parsing cascade

**File**: `guarded/resolver.py`, `guarded/primitives.py`

```
GuardedType.attempt(raw_string)
  ├─ _parse_native    isinstance check           → uncertainty 0.0 (STRICT)
  ├─ _parse_heuristic regex / strip / cast       → uncertainty ~0.1
  ├─ _parse_semantic  LLM call (not implemented) → uncertainty ~0.2
  └─ _parse_knowledge knowledge base             → uncertainty ~0.3+
→ CastingResult(success, data, guarded_data, uncertainty, abstraction_level)
```

For **collections** (GuardedList, GuardedDict, GuardedTuple): `_parse_heuristic` calls `json.loads()` or `ast.literal_eval()` on the string, then recursively applies the inner GuardedType to each element.

### 4b. `pull_extract_data_section` — current limitations

This step currently:
1. Strips `<think>…</think>` reasoning blocks (for DeepSeek/QwQ-style models).
2. Strips the **last** fenced code block (```` ``` ````) if the response ends with one.
3. Strips surrounding `"` or `'`.

> [!WARNING]
> **Known gap**: The current `EMULATE_META_PROMPT` always asks the LLM to return a value "as if writing in REPL" (no explicit instruction on format). Some models wrap the response in `\`\`\`python\`\`\`` spontaneously, others don't. The `pull_extract_data_section` handles the wrapped case only at the end of the string. This causes parsing issues when the LLM generates intermediate reasoning text before the code block.
>
> **Planned improvement**: Add explicit format instruction per return type in the meta-prompt. The generator mode already does this with `is_streaming_generator`.

### 4c. Generator mode: streaming PULL (new)

Instead of `pull()`, the streaming pipeline calls `execute_stream()`:

```
execute_stream(inspection, force_llm_args, item_type)
  └─ push_streaming(inspection, item_type)      → messages (with is_streaming_generator)
  └─ model.generate_stream(messages, **llm_args) → Iterator[str chunk]
  └─ accumulate chunks in buffer
  └─ _extract_next_code_block(buffer)
  │     finds next complete ```python...``` block
  └─ _pull_single_item(inspection, raw_str, item_type)
        temporarily sets inspection.analyse.type = item_type
        calls pull_type_data_section(inspection, raw_str)
        restores original type
  └─ yield typed_item
```

Each `\`\`\`python\`\`\`` block is processed through the full GuardedType pipeline, so `str`, `int`, dataclasses, Pydantic models all work without a dedicated parser.

---

## 5. Retry logic

**File**: `pipelines/simple_pipeline.py` — `execute()` / `execute_async()`

```python
for attempt in range(config.MAX_RETRIES):   # default: 3
    try:
        messages      = push(inspection)
        response_dict = api_call(messages, llm_args)
        response_data = pull(inspection, response_dict)
        return response_data
    except (ValueError, TypeError, UncertaintyError):
        continue   # LLM stochastic nature → retry
raise last_exception
```

The streaming `execute_stream()` does **not** retry — a partial stream cannot be re-tried mid-flight. Errors during item parsing are logged and skipped.

---

## 6. Configuration

**File**: `defaults.py`

```python
config.DefaultModel    # OpenAICompatibleModel(gpt-4o, api.openai.com/v1)
config.DefaultPipeline # OneTurnConversationPipeline(model_list=[DefaultModel])
config.MAX_RETRIES     # 3
```

Multiple models can be loaded from `.models.yaml`. The pipeline picks the first model satisfying all required `ModelCapabilities`.

User-level customisation points:
```python
config.DefaultPipeline.emulate_meta_prompt = MetaPrompt("...")  # replace system prompt
config.DefaultPipeline.user_call_meta_prompt = MetaPrompt("...") # replace user turn
config.DefaultModel.api_parameters["temperature"] = 0.2         # LLM params
my_func.force_template_data = {"chain_of_thought": "Step 1..."}  # per-function prompt data
```

---

## 7. Data-flow diagram

```
User function definition
        │
        ▼
   emulate() called
        │
   get_caller_frame() ──────────────► frame
        │                                │
   identify_function_of_frame() ────────► function_pointer
        │
   hosta_analyze()  ──────────────────► AnalyzedFunction
   (+ detect_caller_context())             { name, args, type, doc }
        │                                  { is_async, is_generator, item_type }
        ▼
  ┌─────────────────────────────────────────────┐
  │              PUSH PHASE                     │
  │  push_detect_missing_types                  │
  │  push_choose_model ──────── ModelCapabilities│
  │  push_check_uncertainty (safe context)      │
  │  push_encode_inspected_data                 │
  │    encode_function() ──► template vars dict │
  │      TypeResolver.resolve(type)             │
  │        → GuardedType.__repr__()             │
  │  push_select_meta_prompts                   │
  │  push_build_messages                        │
  │    EMULATE_META_PROMPT.render(vars)         │
  │    USER_CALL_META_PROMPT.render(vars)       │
  └───────────────────────┬─────────────────────┘
                          │ messages: list[{role, content}]
                          ▼
            Model.api_call() / api_call_async()
            Model.generate_stream()  (generator mode)
                          │
                          │ response_dict / chunk stream
                          ▼
  ┌─────────────────────────────────────────────┐
  │              PULL PHASE                     │
  │  pull_extract_messages  → raw_response str  │
  │  pull_extract_data_section → clean str      │
  │    strip <think>…</think>                   │
  │    strip last ```...``` block               │
  │  pull_type_data_section                     │
  │    TypeResolver.resolve(return_type)        │
  │    GuardedType.attempt(clean_str)           │
  │      _parse_native → _parse_heuristic       │
  │      (json.loads / ast.literal_eval)        │
  │    .unwrap() → native Python value          │
  │  pull_check_uncertainty (safe context)      │
  └───────────────────────┬─────────────────────┘
                          │
                          ▼
              return value / yield item
```

---

## 8. Files quick reference

| File | Role |
|---|---|
| `exec/emulate.py` | Entry point, dispatches to value or generator mode |
| `exec/ask.py` | Simpler entry point without introspection |
| `core/inspection.py` | Frame walking, function pointer identification, `Inspection` object |
| `core/analizer.py` | `hosta_analyze()`, `encode_function()`, `nice_type_name()`, `describe_type_as_python()` |
| `core/meta_prompt.py` | `MetaPrompt` (Jinja2 wrapper), `EMULATE_META_PROMPT`, `USER_CALL_META_PROMPT` |
| `core/base_model.py` | `Model` ABC, `ModelCapabilities`, `api_call`, `generate_stream` |
| `core/caller_context.py` | `CallerContext`, `detect_caller_context()` [NEW] |
| `pipelines/simple_pipeline.py` | `OneTurnConversationPipeline`: push/pull/execute/execute_stream |
| `guarded/resolver.py` | `TypeResolver.resolve()`, `type_returned_data()` |
| `guarded/primitives.py` | `GuardedPrimitive.attempt()`, `CastingResult`, `ProxyWrapper` |
| `guarded/subclassable*.py` | Concrete Guarded types (scalars, collections, callables, etc.) |
| `defaults.py` | `Config`, default model/pipeline setup, `.env` loading |
| `models/OpenAICompatible.py` | `_generate_without_retry`, `generate_stream` [NEW], `get_response_content` |
