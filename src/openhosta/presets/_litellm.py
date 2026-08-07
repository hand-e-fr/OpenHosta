"""LiteLLM presets — proxy unificator, normalises to OpenAI-style params.

LiteLLM translates all params to OpenAI-compatible format, so the presets
use OpenAI-style parameter names. Under the hood, LiteLLM maps to the
appropriate backend params.

Alias mappings:
    litellm.qwen3_6 → equivalent to vllm.qwen3_6 (if self-hosted) or openai.qwen3_6 (if via proxy)
    litellm.claude → equivalent to anthropic.claude (via proxy)
    litellm.gpt4 → equivalent to openai.gpt4 (direct)
"""

from __future__ import annotations

from openhosta.presets._capabilities import (
    _IntersectionCaps, _B_LiteLLM, _M_QWEN3_6, _M_LLAMA, _M_MISTRAL,
    _M_CLAUDE, _M_GPT4, _M_GEMINI,
)
from openhosta.presets import PresetDict


# -- Qwen 3.6 --

class _LL_QWEN3_6_Thinking:
    """LiteLLM: Qwen 3.6 thinking — translated from backend params to OpenAI style."""
    def __init__(self) -> None:
        object.__setattr__(self, "disabled", PresetDict({"chat_template_kwargs": {"enable_thinking": False}}))
        object.__setattr__(self, "enabled", PresetDict({"chat_template_kwargs": {"enable_thinking": True}}))
        object.__setattr__(self, "minimal", PresetDict({"chat_template_kwargs": {"thinking_budget_tokens": 128}}))
        object.__setattr__(self, "low", PresetDict({"chat_template_kwargs": {"thinking_budget_tokens": 1024}}))
        object.__setattr__(self, "medium", PresetDict({"chat_template_kwargs": {"thinking_budget_tokens": 4096}}))
        object.__setattr__(self, "high", PresetDict({"chat_template_kwargs": {"thinking_budget_tokens": 8192}}))
        object.__setattr__(self, "max", PresetDict({"chat_template_kwargs": {"thinking_budget_tokens": 16384}}))


class _LL_QWEN3_6_Sampling:
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "general", PresetDict({"temperature": 1.0, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "coding", PresetDict({"temperature": 0.6, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50, "top_k": 10}))


class _LL_QWEN3_6_Length:
    def __init__(self) -> None:
        object.__setattr__(self, "short", PresetDict({"max_tokens": 256}))
        object.__setattr__(self, "medium", PresetDict({"max_tokens": 2048}))
        object.__setattr__(self, "long", PresetDict({"max_tokens": 8192}))


class _LL_QWEN3_6:
    """Qwen 3.6 via LiteLLM proxy — aliases vLLM params."""
    thinking: _LL_QWEN3_6_Thinking
    sampling: _LL_QWEN3_6_Sampling
    length: _LL_QWEN3_6_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _LL_QWEN3_6_Thinking())
        object.__setattr__(self, "sampling", _LL_QWEN3_6_Sampling())
        object.__setattr__(self, "length", _LL_QWEN3_6_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_LiteLLM(), _M_QWEN3_6()))


# -- Llama --

class _LL_LLAMA_Sampling:
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95, "top_k": 50}))
        object.__setattr__(self, "general", PresetDict({"temperature": 0.8, "top_p": 0.95, "top_k": 50}))
        object.__setattr__(self, "coding", PresetDict({"temperature": 0.6, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50, "top_k": 10}))


class _LL_LLAMA_Length(_LL_QWEN3_6_Length):
    """LiteLLM: Llama length."""
    pass


class _LL_LLAMA:
    sampling: _LL_LLAMA_Sampling
    length: _LL_LLAMA_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "sampling", _LL_LLAMA_Sampling())
        object.__setattr__(self, "length", _LL_LLAMA_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_LiteLLM(), _M_LLAMA()))


# -- Mistral --

class _LL_MISTRAL_Sampling:
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95}))
        object.__setattr__(self, "general", PresetDict({"temperature": 0.7, "top_p": 0.9}))
        object.__setattr__(self, "coding", PresetDict({"temperature": 0.6, "top_p": 0.95}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50}))


class _LL_MISTRAL_Length(_LL_QWEN3_6_Length):
    """LiteLLM: Mistral length."""
    pass


class _LL_MISTRAL:
    sampling: _LL_MISTRAL_Sampling
    length: _LL_MISTRAL_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "sampling", _LL_MISTRAL_Sampling())
        object.__setattr__(self, "length", _LL_MISTRAL_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_LiteLLM(), _M_MISTRAL()))


# -- Claude --

class _LL_CLAUDE_Thinking:
    """LiteLLM: Claude thinking — normalised via proxy to OpenAI-style."""
    def __init__(self) -> None:
        object.__setattr__(self, "disabled", PresetDict({"anthropic_thinking": None}))
        object.__setattr__(self, "minimal", PresetDict({"anthropic_thinking": {"budget_tokens": 128}}))
        object.__setattr__(self, "low", PresetDict({"anthropic_thinking": {"budget_tokens": 1024}}))
        object.__setattr__(self, "medium", PresetDict({"anthropic_thinking": {"budget_tokens": 4096}}))
        object.__setattr__(self, "high", PresetDict({"anthropic_thinking": {"budget_tokens": 8192}}))
        object.__setattr__(self, "max", PresetDict({"anthropic_thinking": {"budget_tokens": 16384}}))


class _LL_CLAUDE_Sampling:
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50}))


class _LL_CLAUDE_Length(_LL_QWEN3_6_Length):
    """LiteLLM: Claude length."""
    pass


class _LL_CLAUDE:
    """Claude via LiteLLM proxy — aliases Anthropic params."""
    thinking: _LL_CLAUDE_Thinking
    sampling: _LL_CLAUDE_Sampling
    length: _LL_CLAUDE_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _LL_CLAUDE_Thinking())
        object.__setattr__(self, "sampling", _LL_CLAUDE_Sampling())
        object.__setattr__(self, "length", _LL_CLAUDE_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_LiteLLM(), _M_CLAUDE()))


# -- GPT-4 --

class _LL_GPT4_Sampling:
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95}))
        object.__setattr__(self, "general", PresetDict({"temperature": 1.0, "top_p": 0.95}))
        object.__setattr__(self, "coding", PresetDict({"temperature": 0.6, "top_p": 0.95}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50}))


class _LL_GPT4_Length(_LL_QWEN3_6_Length):
    """LiteLLM: GPT-4 length."""
    pass


class _LL_GPT4:
    """GPT-4 via LiteLLM proxy — aliases OpenAI params."""
    sampling: _LL_GPT4_Sampling
    length: _LL_GPT4_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "sampling", _LL_GPT4_Sampling())
        object.__setattr__(self, "length", _LL_GPT4_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_LiteLLM(), _M_GPT4()))


# -- Gemini --

class _LL_GEMINI_Thinking:
    """LiteLLM: Gemini thinking — normalised via proxy."""
    def __init__(self) -> None:
        object.__setattr__(self, "disabled", PresetDict({"google_thinking_config": {"disable": True}}))
        object.__setattr__(self, "low", PresetDict({"google_thinking_config": {"thinking_budget": {"min_tokens": 1024}}}))
        object.__setattr__(self, "medium", PresetDict({"google_thinking_config": {"thinking_budget": {"min_tokens": 4096}}}))
        object.__setattr__(self, "high", PresetDict({"google_thinking_config": {"thinking_budget": {"min_tokens": 8192}}}))


class _LL_GEMINI_Sampling:
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "general", PresetDict({"temperature": 1.0, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "coding", PresetDict({"temperature": 0.6, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50, "top_k": 10}))


class _LL_GEMINI_Length(_LL_QWEN3_6_Length):
    """LiteLLM: Gemini length."""
    pass


class _LL_GEMINI:
    """Gemini via LiteLLM proxy — aliases Gemini API params."""
    thinking: _LL_GEMINI_Thinking
    sampling: _LL_GEMINI_Sampling
    length: _LL_GEMINI_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _LL_GEMINI_Thinking())
        object.__setattr__(self, "sampling", _LL_GEMINI_Sampling())
        object.__setattr__(self, "length", _LL_GEMINI_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_LiteLLM(), _M_GEMINI()))


# -- LiteLLM backend --

class _LiteLLM:
    """Presets for LiteLLM proxy."""
    qwen3_6: _LL_QWEN3_6
    llama: _LL_LLAMA
    mistral: _LL_MISTRAL
    claude: _LL_CLAUDE
    gpt4: _LL_GPT4
    gemini: _LL_GEMINI

    def __init__(self) -> None:
        object.__setattr__(self, "qwen3_6", _LL_QWEN3_6())
        object.__setattr__(self, "llama", _LL_LLAMA())
        object.__setattr__(self, "mistral", _LL_MISTRAL())
        object.__setattr__(self, "claude", _LL_CLAUDE())
        object.__setattr__(self, "gpt4", _LL_GPT4())
        object.__setattr__(self, "gemini", _LL_GEMINI())


litellm = _LiteLLM()
