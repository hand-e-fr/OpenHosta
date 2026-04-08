<p align="center">
  <img src="docs/logo.png" alt="OpenHosta Logo" width="180"/>
</p>

<h1 align="center">OpenHosta</h1>

<p align="center">
  <strong>The semantic layer for Python.</strong><br/>
  <em>Write what you mean. Python does the rest.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/OpenHosta/"><img src="https://img.shields.io/pypi/v/OpenHosta?color=blue" alt="PyPI Version"/></a>
  <a href="https://pypi.org/project/OpenHosta/"><img src="https://img.shields.io/pypi/pyversions/OpenHosta" alt="Python Versions"/></a>
  <a href="https://github.com/hand-e-fr/OpenHosta/blob/main/LICENSE"><img src="https://img.shields.io/github/license/hand-e-fr/OpenHosta" alt="License"/></a>
  <a href="https://github.com/hand-e-fr/OpenHosta/actions/workflows/quality_check.yml"><img src="https://github.com/hand-e-fr/OpenHosta/actions/workflows/quality_check.yml/badge.svg" alt="CI Status"/></a>
</p>

---

OpenHosta integrates Large Language Models directly into Python as native functions. Define a function with type hints and a docstring — OpenHosta uses AI to implement it. No DSL, no wrappers, just Python.

```python
from OpenHosta import emulate

def translate(text: str, language: str) -> str:
    """Translates the text into the specified language."""
    return emulate()

print(translate("Hello World!", "French"))
# 'Bonjour le monde !'
```

OpenHosta also enables **semantic testing** — evaluate conditions that require cultural knowledge or fuzzy logic, something traditional `assert` statements can never do:

```python
from OpenHosta import test

sentence = "You are an nice person."

if test(f"this contains an insult: {sentence}"):
    print("The sentence is considered an insult.")
else:
    print("The sentence is not considered an insult.")
# The sentence is not considered an insult.
```

## Why OpenHosta?

- **Zero DSL** — Pure Python syntax. Your functions stay readable, testable, and IDE-friendly.
- **Type-safe** — Guarded types validate LLM output against your annotations (`int`, `dict`, `Enum`, `Pydantic`, `Callable`…).
- **Model-agnostic** — Works with OpenAI, Ollama, Azure, vLLM — any OpenAI-compatible endpoint.
- **Runs offline** — Full local execution with [Ollama](https://ollama.com/). Your data stays private.
- **Production-ready** — Uncertainty tracking, cost tracking, audit mode, and async support built-in.

## Installation

```sh
pip install OpenHosta
```

> We recommend using a virtual environment (`python -m venv .venv`).
> See the full [installation guide](https://github.com/hand-e-fr/OpenHosta/blob/main/docs/installation.md) for local model setup, optional dependencies, and troubleshooting.

## Quick Start

### Option A: Local Execution (Ollama)

Ensure you have [Ollama installed](https://ollama.com/) and run `ollama run qwen3.5:4b` in your terminal.

```python
from OpenHosta import emulate, OpenAICompatibleModel, config

# 1. Point OpenHosta to your local Ollama instance
local_model = OpenAICompatibleModel(
    model_name="qwen3.5:4b",
    base_url="http://localhost:11434/v1",
    api_key="none"  # Ollama does not require a key
)
config.DefaultModel = local_model

# 2. Define and call your function
def translate(text: str, language: str) -> str:
    """Translates the text into the specified language."""
    return emulate()

print(translate("Hello World!", "French"))
# 'Bonjour le monde !'
```

### Option B: Remote API (OpenAI)

Create a `.env` file in your project directory:

```env
OPENHOSTA_DEFAULT_MODEL_NAME="gpt-4.1"
OPENHOSTA_DEFAULT_MODEL_API_KEY="your-api-key-here"
```

```python
from OpenHosta import emulate

def translate(text: str, language: str) -> str:
    """Translates the text into the specified language."""
    return emulate()

print(translate("Hello World!", "French"))
# 'Bonjour le monde !'
```

## What Can You Do?

| Feature | Description |
|---------|-------------|
| [`emulate`](https://github.com/hand-e-fr/OpenHosta/blob/main/docs/core_functions.md) | AI-implemented functions from docstrings |
| [`emulate_async`](https://github.com/hand-e-fr/OpenHosta/blob/main/docs/core_functions.md) | Non-blocking async variant for concurrency |
| [`emulate_iterator`](https://github.com/hand-e-fr/OpenHosta/blob/main/docs/core_functions.md) | Streaming results via lazy generators |
| [`closure`](https://github.com/hand-e-fr/OpenHosta/blob/main/docs/core_functions.md) | Semantic lambda functions |
| [`test`](https://github.com/hand-e-fr/OpenHosta/blob/main/docs/core_functions.md) | Fuzzy logic / semantic boolean tests |
| [Types & Pydantic](https://github.com/hand-e-fr/OpenHosta/blob/main/docs/types_and_pydantic.md) | `int`, `dict`, `Enum`, `dataclass`, `Pydantic`, `Callable`… |
| [Safe Context](https://github.com/hand-e-fr/OpenHosta/blob/main/docs/safe_context_and_uncertainty.md) | Uncertainty tracking & error handling |
| [Image input](https://github.com/hand-e-fr/OpenHosta/blob/main/docs/examples/ocr_local_ollama.md) | Pass `PIL.Image` directly to functions |

📖 **[Full Documentation](https://github.com/hand-e-fr/OpenHosta/blob/main/docs/doc.md)** · 📝 **[Changelog](https://github.com/hand-e-fr/OpenHosta/blob/main/CHANGELOG.md)** · 🧪 **[Examples](https://github.com/hand-e-fr/OpenHosta/tree/main/tests/)**

## Contributing

We warmly welcome contributions! Please refer to our [Contribution Guide](https://github.com/hand-e-fr/OpenHosta/blob/main/CONTRIBUTING.md) and [Code of Conduct](https://github.com/hand-e-fr/OpenHosta/blob/main/CODE_OF_CONDUCT.md).

Browse existing [issues](https://github.com/hand-e-fr/OpenHosta/issues) to find contribution ideas.

## License

MIT License — see [LICENSE](https://github.com/hand-e-fr/OpenHosta/blob/main/LICENSE) for details.

## Authors

- **Emmanuel Batt** — Manager and Coordinator, Founder of Hand-e
- **William Jolivet** — DevOps, SysAdmin
- **Léandre Ramos** — AI Developer
- **Merlin Devillard** — UX Designer, Product Owner

GitHub: https://github.com/hand-e-fr/OpenHosta

---

**The future of development is human.** — The OpenHosta Team
