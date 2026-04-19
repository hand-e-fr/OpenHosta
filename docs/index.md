# OpenHosta Documentation

**Version 4.2** · [GitHub](https://github.com/hand-e-fr/OpenHosta) · [PyPI](https://pypi.org/project/OpenHosta/)

Welcome to the **OpenHosta** documentation. OpenHosta is the semantic layer for Python — it transforms human language and type annotations into executable, type-safe Python functions powered by Large Language Models.

---

## Quick Navigation

### 🚀 [Getting Started](getting_started.md)
Set up your environment, configure a local or remote model, and run your first `emulate()` call.

### ⚙️ [Core Functions](core_functions.md)
Learn about `emulate`, `emulate_async`, `emulate_iterator`, `closure`, `ask`, and `test`.

### 🔄 [Streaming & Iterators](streaming.md)
Stream raw tokens with `ask_stream`, or yield structured Python objects one-by-one with `Iterator` return types and `emulate_iterator`.

### 🔧 [Models & Setup](models_and_setup.md)
Connect any OpenAI-compatible endpoint (Ollama, vLLM, Azure OpenAI), customize prompts, enable audit mode, and track costs.

### 🧩 [Types & Pydantic Validation](types_and_pydantic.md)
OpenHosta natively supports `int`, `str`, `List`, `Dict`, `Enum`, `dataclass`, `Pydantic V2`, and even [`Callable`](callables.md) return types.

### 🛡️ [Safe Context & Error Handling](safe_context_and_uncertainty.md)
Handle uncertainty, catch ambiguous LLM responses, and build robust production workflows.

### 📐 [Guarded Types](guarded.md)
Deep dive into OpenHosta's type validation and conversion system with configurable tolerance.

---

## Cookbook

| Example | Description |
|---------|-------------|
| 📚 [Text Classification](examples/text_classification.md) | Classify text into `Enum` states |
| 🗃️ [Data Extraction](examples/data_extraction.md) | Populate `dataclass` / `Pydantic` from unstructured text |
| 👁️ [Local OCR](examples/ocr_local_ollama.md) | Image processing with `PIL.Image` + Ollama |
| ⚡ [Parallel Processing](examples/parallel_processing.md) | Async batch workloads with `emulate_async` |
| 🔄 [Streaming & Iterators](streaming.md) | Stream tokens or yield typed objects with `Iterator` |

---

## Compatibility

- **Python**: 3.10, 3.11, 3.12, 3.13, 3.14 ([details](compatibility_table.md))
- **Models**: OpenAI (GPT-4.1, GPT-5), Ollama (Qwen, Mistral), Azure, vLLM ([type matrix](compat_matrix_types.md))

---

## Contributing

We welcome contributions! See our [Contribution Guide](https://github.com/hand-e-fr/OpenHosta/blob/main/CONTRIBUTING.md) and [Code of Conduct](https://github.com/hand-e-fr/OpenHosta/blob/main/CODE_OF_CONDUCT.md).

*OpenHosta is licensed under the [MIT License](https://github.com/hand-e-fr/OpenHosta/blob/main/LICENSE).*
