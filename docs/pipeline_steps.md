# Detailed Pipeline Steps

This document provides a technical breakdown of the OpenHosta execution pipeline, detailing the responsibility of each step.

## 1. Analysis Phase (`core/analizer.py`)
- **Responsibility**: Inspect the calling function's signature and documentation.
- **Key Step**: `hosta_analyze()`
  - Uses `inspect.signature` to get parameters.
  - Uses `typing.get_type_hints` to resolve annotations.
  - Generates an `AnalyzedFunction` dataclass.

## 2. Preparation (Push Phase - `pipelines/simple_pipeline.py`)
- **`push_detect_missing_types`**: Fills in `Any` or `str` if annotations are missing.
- **`push_choose_model`**: Matches required capabilities (Text, Image, JSON, Logprobs) against available models.
- **`push_check_uncertainty` (Safe Context)**: 
  - If inside a `safe()` block, it injects the `seed` to ensure reproducibility.
  - It automatically injects `{"logprobs": True, "top_logprobs": 20}` into the LLM parameters if the model supports it.
- **`push_encode_inspected_data`**: Calls `encode_function` to transform the analysis into prompt-ready snippets (docstrings, type definitions via `TypeResolver`).
- **`push_select_meta_prompts`**: Chooses the appropriate system and user templates.
- **`push_build_messages`**: Renders the templates with the encoded data to produce the final payload for the LLM API.

## 3. Execution (`core/base_model.py`)
- **Responsibility**: Send the payload to the LLM and receive the raw response.
- **Retries**: The pipeline handles retries here if subsequent parsing fails.

## 4. Processing (Pull Phase - `pipelines/simple_pipeline.py`)
- **`pull_extract_messages`**: Retrieves the text content from the API response format.
- **`pull_extract_data_section`**: Identifies "Thinking" vs "Answer" blocks (crucial for reasoning models).
- **`pull_type_data_section`**:
  - Calls `TypeResolver.resolve()` to get the executable `GuardedPrimitive`.
  - Calls `guarded_type.attempt()` to parse the string into a Python object.
  - Performs `.unwrap()` if a native type was expected (unless a Guarded type was explicitly requested).
- **`pull_check_uncertainty`**: 
  - If inside a `safe()` block, it extracts the logprobs from the response.
  - For Enums, it uses `get_enum_logprobes` to calculate probabilities for all valid members.
  - For other types, it uses `get_certainty` to estimate the confidence of the generated answer.
  - Updates the `cumulated_uncertainty` in the safety context and raises `UncertaintyError` if the threshold is exceeded.
