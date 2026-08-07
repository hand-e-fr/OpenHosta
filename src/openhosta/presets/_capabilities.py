"""Backend ∩ Model capability intersection.

Each model preset exposes ``.capabilities.supports`` — a dict of bools
representing the intersection of what the model can do and what the
backend API can express.

Example:
    vllm.qwen3_6.capabilities.supports["thinking"]  # True
    vllm.claude.capabilities.supports["vision"]      # False (vLLM lacks vision)
    anthropic.claude.capabilities.supports["vision"]  # True  (Anthropic API supports it)
"""

from __future__ import annotations

_CAPABILITY_KEYS = [
    "thinking", "tool_calling", "structured_output", "logprobs",
    "prompt_caching", "parallel_tool_calls", "vision", "audio",
    "function_calling", "json_schema", "stream_options", "stop_sequences",
]


class _Caps:
    """Base class for capability dicts (both model-side and backend-side)."""
    def __init__(self) -> None:
        object.__setattr__(self, "supports", self._build())

    def _build(self) -> dict[str, bool]:
        raise NotImplementedError  # type: ignore[return]


class _IntersectionCaps:
    """Intersection between backend and model capabilities.

    ``backend.model.capabilities.supports[k]`` is True iff both backend
    and model support feature ``k``.
    """
    def __init__(self, b: _Caps, m: _Caps) -> None:
        intersection = {k: b.supports.get(k, False) and m.supports.get(k, False)
                        for k in _CAPABILITY_KEYS}
        object.__setattr__(self, "supports", intersection)


# ============================================================================
# MODEL CAPABILITIES — what the model itself can do
# ============================================================================

class _M_QWEN3_6(_Caps):
    def _build(self) -> dict[str, bool]:
        return {"thinking": True, "tool_calling": True, "structured_output": True,
                "logprobs": True, "prompt_caching": True, "parallel_tool_calls": True,
                "vision": True, "audio": True, "function_calling": True,
                "json_schema": True, "stream_options": True, "stop_sequences": True}


class _M_LLAMA(_Caps):
    def _build(self) -> dict[str, bool]:
        return {"thinking": False, "tool_calling": True, "structured_output": True,
                "logprobs": True, "prompt_caching": False, "parallel_tool_calls": True,
                "vision": False, "audio": False, "function_calling": True,
                "json_schema": True, "stream_options": True, "stop_sequences": True}


class _M_MISTRAL(_Caps):
    def _build(self) -> dict[str, bool]:
        return {"thinking": False, "tool_calling": True, "structured_output": True,
                "logprobs": True, "prompt_caching": False, "parallel_tool_calls": True,
                "vision": True, "audio": False, "function_calling": True,
                "json_schema": True, "stream_options": True, "stop_sequences": True}


class _M_CLAUDE(_Caps):
    def _build(self) -> dict[str, bool]:
        return {"thinking": True, "tool_calling": True, "structured_output": False,
                "logprobs": False, "prompt_caching": True, "parallel_tool_calls": True,
                "vision": True, "audio": False, "function_calling": False,
                "json_schema": False, "stream_options": True, "stop_sequences": True}


class _M_GPT4(_Caps):
    def _build(self) -> dict[str, bool]:
        return {"thinking": False, "tool_calling": True, "structured_output": True,
                "logprobs": True, "prompt_caching": False, "parallel_tool_calls": True,
                "vision": True, "audio": True, "function_calling": True,
                "json_schema": True, "stream_options": True, "stop_sequences": True}


class _M_OSERIES(_Caps):
    def _build(self) -> dict[str, bool]:
        return {"thinking": True, "tool_calling": False, "structured_output": True,
                "logprobs": False, "prompt_caching": False, "parallel_tool_calls": False,
                "vision": False, "audio": False, "function_calling": False,
                "json_schema": True, "stream_options": True, "stop_sequences": True}


class _M_GEMINI(_Caps):
    def _build(self) -> dict[str, bool]:
        return {"thinking": True, "tool_calling": True, "structured_output": True,
                "logprobs": False, "prompt_caching": True, "parallel_tool_calls": True,
                "vision": True, "audio": True, "function_calling": True,
                "json_schema": True, "stream_options": True, "stop_sequences": True}


# ============================================================================
# BACKEND CAPABILITIES — what the API can express
# ============================================================================

class _B_VLLM(_Caps):
    """vLLM — OpenAI-compatible, supports logprobs, thinking kwargs."""
    def _build(self) -> dict[str, bool]:
        return {"thinking": True, "tool_calling": True, "structured_output": True,
                "logprobs": True, "prompt_caching": False, "parallel_tool_calls": True,
                "vision": False, "audio": False, "function_calling": True,
                "json_schema": True, "stream_options": True, "stop_sequences": True}


class _B_SGLang(_Caps):
    """SGLang — OpenAI-compatible."""
    def _build(self) -> dict[str, bool]:
        return {"thinking": True, "tool_calling": True, "structured_output": True,
                "logprobs": True, "prompt_caching": False, "parallel_tool_calls": True,
                "vision": False, "audio": False, "function_calling": True,
                "json_schema": True, "stream_options": True, "stop_sequences": True}


class _B_Transformers(_Caps):
    """HuggingFace Transformers — local inference, limited to sampling."""
    def _build(self) -> dict[str, bool]:
        return {"thinking": False, "tool_calling": False, "structured_output": True,
                "logprobs": True, "prompt_caching": False, "parallel_tool_calls": False,
                "vision": False, "audio": False, "function_calling": False,
                "json_schema": True, "stream_options": True, "stop_sequences": True}


class _B_Ollama(_Caps):
    """Ollama — OpenAI-compatible endpoint."""
    def _build(self) -> dict[str, bool]:
        return {"thinking": True, "tool_calling": True, "structured_output": True,
                "logprobs": False, "prompt_caching": False, "parallel_tool_calls": True,
                "vision": False, "audio": False, "function_calling": True,
                "json_schema": True, "stream_options": True, "stop_sequences": True}


class _B_OpenAI(_Caps):
    """OpenAI native API."""
    def _build(self) -> dict[str, bool]:
        return {"thinking": False, "tool_calling": True, "structured_output": True,
                "logprobs": True, "prompt_caching": False, "parallel_tool_calls": True,
                "vision": True, "audio": True, "function_calling": True,
                "json_schema": True, "stream_options": True, "stop_sequences": True}


class _B_OpenAI_O(_Caps):
    """OpenAI o-series — reasoning effort instead of temperature."""
    def _build(self) -> dict[str, bool]:
        return {"thinking": True, "tool_calling": False, "structured_output": True,
                "logprobs": False, "prompt_caching": False, "parallel_tool_calls": False,
                "vision": False, "audio": False, "function_calling": False,
                "json_schema": True, "stream_options": True, "stop_sequences": True}


class _B_Anthro(_Caps):
    """Anthropic Messages API."""
    def _build(self) -> dict[str, bool]:
        return {"thinking": True, "tool_calling": True, "structured_output": False,
                "logprobs": False, "prompt_caching": True, "parallel_tool_calls": True,
                "vision": True, "audio": False, "function_calling": False,
                "json_schema": False, "stream_options": True, "stop_sequences": True}


class _B_Gemini(_Caps):
    """Google Gemini API."""
    def _build(self) -> dict[str, bool]:
        return {"thinking": True, "tool_calling": True, "structured_output": True,
                "logprobs": False, "prompt_caching": True, "parallel_tool_calls": True,
                "vision": True, "audio": True, "function_calling": True,
                "json_schema": True, "stream_options": True, "stop_sequences": True}


class _B_LiteLLM(_Caps):
    """LiteLLM proxy — normalises to OpenAI-style params.

    Conservatively supports everything; actual intersection depends on
    the underlying backend+model combination.
    """
    def _build(self) -> dict[str, bool]:
        return {"thinking": True, "tool_calling": True, "structured_output": True,
                "logprobs": True, "prompt_caching": True, "parallel_tool_calls": True,
                "vision": True, "audio": True, "function_calling": True,
                "json_schema": True, "stream_options": True, "stop_sequences": True}


class _B_OpenRouter(_Caps):
    """OpenRouter — OpenAI-compatible gateway to multiple providers."""
    def _build(self) -> dict[str, bool]:
        return {"thinking": True, "tool_calling": True, "structured_output": True,
                "logprobs": True, "prompt_caching": True, "parallel_tool_calls": True,
                "vision": True, "audio": True, "function_calling": True,
                "json_schema": True, "stream_options": True, "stop_sequences": True}


class _B_Scaleway(_Caps):
    """Scaleway ML — vLLM-compatible + Scaleway-specific extensions."""
    def _build(self) -> dict[str, bool]:
        return {"thinking": True, "tool_calling": True, "structured_output": True,
                "logprobs": True, "prompt_caching": False, "parallel_tool_calls": True,
                "vision": False, "audio": False, "function_calling": True,
                "json_schema": True, "stream_options": True, "stop_sequences": True}
