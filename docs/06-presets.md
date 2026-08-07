# Presets — OpenHosta V5

## Overview

`openhosta.presets` provides pre-configured parameter sets for LLM backends.
Chain presets with `|` operators to compose request bodies.

```python
from openhosta.presets import vllm, anthropic, openai

body = vllm.qwen3_6.thinking.disabled | vllm.qwen3_6.sampling.coding
body = anthropic.claude.thinking.medium | anthropic.claude.sampling.creative
body = openai.o_series.reasoning.high
```

## Hierarchy

```
openhosta.presets/
├── vllm/                └── qwen3_6 / llama / mistral / claude
├── sglang/              └── qwen3_6 / llama / mistral / claude
├── transformers/        └── qwen3_6 / llama / claude
├── ollama/              └── qwen3_6 / llama / mistral / claude
├── openai/              └── gpt4 / o_series
├── anthropic/           └── claude / bedrock
├── gemini/              └── gemini
├── litellm/             └── (aliases to all backends)
├── openrouter/          └── (gateway presets)
└── scaleway/            └── (vLLM + extensions)
```

## Preset Families

### Thinking / Reasoning

Control the model's chain-of-thought budget.

| Preset   | Effect | Budget |
|----------|--------|--------|
| `disabled` | No thinking | 0 |
| `minimal` | Quick reasoning | 128 |
| `low` | Moderate | 1024 |
| `medium` | Standard | 4096 |
| `high` | Extended | 8192 |
| `max` | Maximum | 16384 |

Cross-backend equivalence:

| Preset | vLLM / SGLang | Ollama | OpenAI o-series | Anthropic | Gemini |
|--------|---------------|--------|-----------------|-----------|--------|
| disabled | `enable_thinking=False` | `thinking_enabled=False` | — | `thinking=None` | `thinking_budget=0` |
| minimal | `budget_tokens=128` | `thinking_budget=128` | `reasoning.effort=low` | `budget_tokens=128` | `min_tokens=128` |
| medium | `budget_tokens=4096` | `thinking_budget=4096` | `reasoning.effort=medium` | `budget_tokens=4096` | `min_tokens=4096` |
| max | `budget_tokens=16384` | `thinking_budget=16384` | — | `budget_tokens=16384` | — |

### Sampling

Control temperature, top_p, top_k, and penalties.

| Preset | temp | top_p | top_k | Description |
|--------|------|-------|-------|-------------|
| `creative` | 1.0 | 0.95 | 20 | Maximum diversity |
| `general` | 1.0 | 0.95 | 20 | Balanced defaults |
| `coding` | 0.6 | 0.95 | 20 | Code generation |
| `instruct` | 0.7 | 0.80 | 20 | Instruction following |
| `precise` | 0.2 | 0.50 | 10 | Deterministic output |

Same values across all backends.

### Output Length

| Preset | max_tokens |
|--------|------------|
| `short` | 256 |
| `medium` | 2048 |
| `long` | 8192 |

### Safety / Content Filtering

Backend-specific implementations with common names:

| Preset | vLLM / SGLang | Anthropic | OpenAI / Gemini |
|--------|---------------|-----------|-----------------|
| `strict` | `presence_penalty=2.0` | `safety=strict` | `content_filter=strict` |
| `relaxed` | `presence_penalty=0.0` | `safety=relaxed` | `content_filter=none` |
| `off` | `frequency_penalty=0.0` | `safety=off` | — |

## Capabilities — Backend ∩ Model

Each `backend.model` exposes `.capabilities.supports`, a dict of bools
representing the intersection of what the model can do and what the
backend API can express.

```python
from openhosta.presets import vllm, anthropic

# vLLM ∩ Qwen 3.6
vllm.qwen3_6.capabilities.supports["thinking"]   # True
vllm.qwen3_6.capabilities.supports["vision"]      # False (vLLM lacks vision API)

# Anthropic ∩ Claude
anthropic.claude.capabilities.supports["vision"]  # True (both support it)
anthropic.claude.capabilities.supports["logprobs"] # False (Anthropic lacks logprobs)
```

### Capability matrix — Qwen 3.6

| Feature | vLLM | SGLang | Ollama | OpenAI | Anthropic | Gemini |
|---------|------|--------|--------|--------|-----------|--------|
| thinking | T | T | T | T | T | T |
| tool_calling | T | T | T | T | T | T |
| structured_output | T | T | T | T | F | T |
| logprobs | T | T | F | T | F | F |
| prompt_caching | F | F | F | F | T | T |
| vision | F | F | F | T | T | T |
| audio | F | F | F | T | F | T |

### Capability guard pattern

Check capabilities before applying presets:

```python
if vllm.qwen3_6.capabilities.supports["thinking"]:
    body = vllm.qwen3_6.thinking.disabled | vllm.qwen3_6.sampling.coding
```

## Chaining with `|`

`PresetDict` supports `|` and `|=` for composable requests:

```python
body = (vllm.qwen3_6.thinking.disabled
        | vllm.qwen3_6.sampling.coding
        | vllm.qwen3_6.length.short)

# Merge with raw dict
body | {"seed": 42, "stop_sequences": ["\n"]}
```

## Backend-specific

### Scaleway ML

Inherits vLLM presets + Scaleway-specific extensions:

```python
from openhosta.presets import scaleway

body = scaleway.qwen3_6.thinking.sw_accelerated  # GPU cache + thinking
```

### Anthropic Bedrock

Minimum `budget_tokens = 1024`:

```python
from openhosta.presets import anthropic

body = anthropic.claude.bedrock.low  # budget_tokens=1024
```

### LiteLLM

Normalizes all params to OpenAI-style:

```python
litellm.qwen3_6.thinking.disabled   # → chat_template_kwargs
litellm.claude.thinking.max         # → anthropic_thinking
litellm.gpt4.sampling.creative      # → temperature, top_p
```

### OpenRouter

All models use OpenAI-compatible params:

```python
openrouter.qwen3_6.thinking.disabled | openrouter.qwen3_6.sampling.coding
openrouter.claude.thinking.max
openrouter.o_series.reasoning.high
```

## Integration with BackendModel

Pass presets to `BackendModel.body`:

```python
from openhosta import BackendModel
from openhosta.presets import vllm

model = BackendModel(
    provider="ikoula",
    model_name="Qwen3.6-8B",
    base_url="http://ikoula.example.com/v1",
    api_key="none",
    body=vllm.qwen3_6.thinking.disabled | vllm.qwen3_6.sampling.coding,
)
```

## Complete Example

```python
from openhosta import Agent, BackendModel, infer
from openhosta.presets import vllm

model = BackendModel(
    provider="ikoula",
    model_name="Qwen3.6-8B",
    base_url="http://ikoula.example.com/v1",
    api_key="none",
    body=vllm.qwen3_6.thinking.disabled | vllm.qwen3_6.sampling.coding,
)

@model.compile()
class Coder(Agent):
    @model.infer()
    def generate_code(self, spec: str) -> str:
        """Generate Python code from specification."""
        ...

agent = Coder()
agent.recruit()
code = agent.get("Create a REST API with FastAPI")
agent.free()
```
