# OpenHosta Documentation Hub

Documentation for version: **4.2**

Welcome to the **OpenHosta** documentation hub. Here you'll find everything you need to leverage Large Language Models (LLMs) natively within your Python projects. OpenHosta transforms human language and semantic structures into pure, executable Python functions.


---

## Thematic Documentation

We have divided the documentation into focused, digestible themes allowing you to deep-dive into the precise framework concepts you are looking for.

### 1. [Getting Started](getting_started.md)
Start here to understand what OpenHosta uniquely brings to the Python ecosystem. Learn about basic environmental setup, environment variables, first steps, and how you can run models locally or in the cloud.

### 2. [Core Functions](core_functions.md)
Discover the fundamental backbone of OpenHosta. Learn about the `emulate` function in synchronous and asynchronous modes, how to use `ask` for simple tasks, and `closure` for LLM-powered lambda alternatives.

### 3. [Models and Setup](models_and_setup.md)
For those needing full control. Connect any endpoint (Ollama, vLLM, Azure OpenAI), configure `OpenAICompatibleModel` classes from scratch, customize MetaPrompts, read about Audit modes, and keep track of your API costs.

### 4. [Types & Pydantic Validation](types_and_pydantic.md)
Discover the power of generative extraction. OpenHosta intrinsically knows how to respond via standard Python Typing lists/dicts, Enums, and even complete `Pydantic V2` objects. Ensure validation and semantic safety dynamically.

Starting from version **4.1**, you can even return executable logic using [**Generative Callables**](callables.md).

### 5. [Safe Context & Error Handling](safe_context_and_uncertainty.md)
Building bullet-proof workflows around non-deterministic intelligence. Catch context uncertainties, handle safety loops, and understand `UncertaintyError`.

---

## Cookbook Examples

Take off your conceptual hat and observe OpenHosta in action through functional examples!

- 📚 [**Text Classification:**](examples/text_classification.md) Sorting streams of text directly into rigidly typed `Enum` states.
- 🗃️ [**Data Extraction:**](examples/data_extraction.md) Populating massive `Dataclasses` and `Pydantic` modules straight from unstructured text blobs.
- 👁️ [**Local OCR with Ollama:**](examples/ocr_local_ollama.md) Passing images using `PIL.Image` directly into `emulate`, performing OCR securely and locally using `glm-ocr`.
- ⚡ [**Parallel Processing:**](parallel_processing.md) Running asynchronous workloads, parsing dataclasses like invoices, and batching prompts.
- 🌊 [**Streaming & Iteration:**](streaming.md) Receiving results token-by-token or item-by-item to improve UX and handle long responses.

---

## Contribution & Legal

If you like the project and are thinking of contributing, please refer to our [Contribution Guide](https://github.com/hand-e-fr/OpenHosta/blob/main/CONTRIBUTING.md) and respect our [Code of Conduct](https://github.com/hand-e-fr/OpenHosta/blob/main/CODE_OF_CONDUCT.md).

*Deploying AI in production carries significant responsibilities. Refer to [Getting Started](getting_started.md) for legal framework (GDPR, IA Act) and prompt injection safety disclaimers.*
