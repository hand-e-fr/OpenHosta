"""Parameter presets for LLM backends (vLLM, SGLang, etc.) and models.

Hierarchy:  backend.model.family.preset
            └── capabilities: backend ∩ model (feature support intersection)

Same preset names across backends → equivalent semantic effect, backend-specific params.

Usage:
    from openhosta.presets import vllm, openai, anthropic
    body = vllm.qwen3_6.thinking.disabled | vllm.qwen3_6.sampling.coding
    cap  = vllm.qwen3_6.capabilities.supports["thinking"]  # bool
"""

from __future__ import annotations
from typing import Any


# ============================================================================
# PRESET DICT — chaining dict
# ============================================================================

class PresetDict(dict):
    """dict subclass supporting | and |= for preset chaining.

    Examples:
        body = vllm.qwen3_6.thinking.disabled | vllm.qwen3_6.sampling.coding
    """

    def __or__(self, other: dict[str, Any]) -> PresetDict:  # type: ignore[override]
        result = PresetDict(self)
        result.update(other)
        return result

    def __ror__(self, other: dict[str, Any]) -> PresetDict:
        result = PresetDict(other)
        result.update(self)
        return result

    def __ior__(self, other: dict[str, Any]) -> PresetDict:
        dict.update(self, other)
        return self


# ============================================================================
# BACKEND INSTANCES
# ============================================================================

from openhosta.presets._vllm import vllm  # noqa: E402
from openhosta.presets._sglang import sglang  # noqa: E402
from openhosta.presets._transformers import transformers  # noqa: E402
from openhosta.presets._ollama import ollama  # noqa: E402
from openhosta.presets._openai import openai  # noqa: E402
from openhosta.presets._anthropic import anthropic  # noqa: E402
from openhosta.presets._gemini import gemini  # noqa: E402
from openhosta.presets._litellm import litellm  # noqa: E402
from openhosta.presets._openrouter import openrouter  # noqa: E402
from openhosta.presets._scaleway import scaleway  # noqa: E402
from openhosta.presets._capabilities import (  # noqa: E402
    _Caps,
    _IntersectionCaps,
    _M_QWEN3_6, _M_LLAMA, _M_MISTRAL, _M_CLAUDE, _M_GPT4, _M_OSERIES, _M_GEMINI,
    _B_VLLM, _B_SGLang, _B_Transformers, _B_Ollama,
    _B_OpenAI, _B_OpenAI_O, _B_Anthro, _B_Gemini,
    _B_LiteLLM, _B_OpenRouter, _B_Scaleway,
)

__all__ = [
    "PresetDict",
    "vllm", "sglang", "transformers", "ollama",
    "openai", "anthropic", "gemini",
    "litellm", "openrouter", "scaleway",
    "_Caps", "_IntersectionCaps",
    "_M_QWEN3_6", "_M_LLAMA", "_M_MISTRAL", "_M_CLAUDE",
    "_M_GPT4", "_M_OSERIES", "_M_GEMINI",
    "_B_VLLM", "_B_SGLang", "_B_Transformers", "_B_Ollama",
    "_B_OpenAI", "_B_OpenAI_O", "_B_Anthro", "_B_Gemini",
    "_B_LiteLLM", "_B_OpenRouter", "_B_Scaleway",
]
