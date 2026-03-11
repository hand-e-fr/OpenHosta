# OpenHosta V4 Changelog

This document outlines the major evolutions and new features added to OpenHosta since version 3.0.4, preparing for the V4 release.

## Major Evolutions

### Guarded Types and Validation System
- **Guarded Primitives & Collections**: Introduced a comprehensive guarded types system (`GuardedPrimitive`, parameterized collections, dataclasses, `Union`, `Complex`, `Bytes`, etc.) to enforce structural and semantic validation on LLM outputs.
- **Enhanced Tolerance**: Improved type handling and tolerance within guarded classes, enabling multi-level validation pipelines for robust applications.

### Pydantic V2 Integration
- Seamless integration of Pydantic V2 within the semantic types system.
- Enforced non-hashability for fuzzy equality in semantic types.
- Comprehensive tests added for semantic scalars and collections.

### Native Ollama Integration
- Added native compatibility for local text generation and embeddings using Ollama.
- Introduced `OllamaModel` to seamlessly interface with local API instances (e.g., `qwen3.5:4b`, `gemma3:4b`).

### Semantic Embeddings & Clustering
- Enhancements to semantic embeddings by integrating type-based contexts to improve clustering accuracy.
- Implemented a generic embedding API call for models, integrating it natively into the core engine and semantic collections.
- Added factory method `create_semantic_type`.

### Generative Data Extraction Engines
- Implemented a powerful generative data extraction and conversion engine utilizing multiple strategies to reliably extract structured data from unstructured context.
