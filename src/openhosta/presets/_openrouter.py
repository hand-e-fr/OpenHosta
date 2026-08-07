"""OpenRouter presets — marketplace gateway, OpenAI-compatible API."""

from __future__ import annotations

from openhosta.presets._capabilities import (
    _IntersectionCaps, _B_OpenRouter, _M_QWEN3_6, _M_LLAMA, _M_MISTRAL,
    _M_CLAUDE, _M_GPT4, _M_OSERIES, _M_GEMINI,
)
from openhosta.presets import PresetDict


# -- Qwen 3.6 --

class _OR_QWEN3_6_Thinking:
    """OpenRouter: Qwen 3.6 thinking — normalised to OpenAI-style params."""
    def __init__(self) -> None:
        object.__setattr__(self, "disabled", PresetDict({"chat_template_kwargs": {"enable_thinking": False}}))
        object.__setattr__(self, "enabled", PresetDict({"chat_template_kwargs": {"enable_thinking": True}}))
        object.__setattr__(self, "minimal", PresetDict({"chat_template_kwargs": {"thinking_budget_tokens": 128}}))
        object.__setattr__(self, "low", PresetDict({"chat_template_kwargs": {"thinking_budget_tokens": 1024}}))
        object.__setattr__(self, "medium", PresetDict({"chat_template_kwargs": {"thinking_budget_tokens": 4096}}))
        object.__setattr__(self, "high", PresetDict({"chat_template_kwargs": {"thinking_budget_tokens": 8192}}))
        object.__setattr__(self, "max", PresetDict({"chat_template_kwargs": {"thinking_budget_tokens": 16384}}))


class _OR_QWEN3_6_Sampling:
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "general", PresetDict({"temperature": 1.0, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "coding", PresetDict({"temperature": 0.6, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50, "top_k": 10}))


class _OR_QWEN3_6_Length:
    def __init__(self) -> None:
        object.__setattr__(self, "short", PresetDict({"max_tokens": 256}))
        object.__setattr__(self, "medium", PresetDict({"max_tokens": 2048}))
        object.__setattr__(self, "long", PresetDict({"max_tokens": 8192}))


class _OR_QWEN3_6:
    """Qwen 3.6 via OpenRouter — OpenAI-compatible params."""
    thinking: _OR_QWEN3_6_Thinking
    sampling: _OR_QWEN3_6_Sampling
    length: _OR_QWEN3_6_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _OR_QWEN3_6_Thinking())
        object.__setattr__(self, "sampling", _OR_QWEN3_6_Sampling())
        object.__setattr__(self, "length", _OR_QWEN3_6_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_OpenRouter(), _M_QWEN3_6()))


# -- Llama --

class _OR_LLAMA_Sampling:
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95, "top_k": 50}))
        object.__setattr__(self, "general", PresetDict({"temperature": 0.8, "top_p": 0.95, "top_k": 50}))
        object.__setattr__(self, "coding", PresetDict({"temperature": 0.6, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50, "top_k": 10}))


class _OR_LLAMA_Length(_OR_QWEN3_6_Length):
    pass


class _OR_LLAMA:
    sampling: _OR_LLAMA_Sampling
    length: _OR_LLAMA_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "sampling", _OR_LLAMA_Sampling())
        object.__setattr__(self, "length", _OR_LLAMA_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_OpenRouter(), _M_LLAMA()))


# -- Mistral --

class _OR_MISTRAL_Sampling:
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95}))
        object.__setattr__(self, "general", PresetDict({"temperature": 0.7, "top_p": 0.9}))
        object.__setattr__(self, "coding", PresetDict({"temperature": 0.6, "top_p": 0.95}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50}))


class _OR_MISTRAL_Length(_OR_QWEN3_6_Length):
    pass


class _OR_MISTRAL:
    sampling: _OR_MISTRAL_Sampling
    length: _OR_MISTRAL_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "sampling", _OR_MISTRAL_Sampling())
        object.__setattr__(self, "length", _OR_MISTRAL_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_OpenRouter(), _M_MISTRAL()))


# -- Claude --

class _OR_CLAUDE_Thinking:
    """OpenRouter: Claude thinking — normalised via OpenAI-style thinking param."""
    def __init__(self) -> None:
        object.__setattr__(self, "disabled", PresetDict({"thinking": None}))
        object.__setattr__(self, "minimal", PresetDict({"thinking": {"budget_tokens": 128}}))
        object.__setattr__(self, "low", PresetDict({"thinking": {"budget_tokens": 1024}}))
        object.__setattr__(self, "medium", PresetDict({"thinking": {"budget_tokens": 4096}}))
        object.__setattr__(self, "high", PresetDict({"thinking": {"budget_tokens": 8192}}))
        object.__setattr__(self, "max", PresetDict({"thinking": {"budget_tokens": 16384}}))


class _OR_CLAUDE_Sampling:
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50}))


class _OR_CLAUDE_Length(_OR_QWEN3_6_Length):
    pass


class _OR_CLAUDE:
    """Claude via OpenRouter — OpenAI-compatible params."""
    thinking: _OR_CLAUDE_Thinking
    sampling: _OR_CLAUDE_Sampling
    length: _OR_CLAUDE_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _OR_CLAUDE_Thinking())
        object.__setattr__(self, "sampling", _OR_CLAUDE_Sampling())
        object.__setattr__(self, "length", _OR_CLAUDE_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_OpenRouter(), _M_CLAUDE()))


# -- GPT-4 --

class _OR_GPT4_Sampling:
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95}))
        object.__setattr__(self, "general", PresetDict({"temperature": 1.0, "top_p": 0.95}))
        object.__setattr__(self, "coding", PresetDict({"temperature": 0.6, "top_p": 0.95}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50}))


class _OR_GPT4_Length(_OR_QWEN3_6_Length):
    pass


class _OR_GPT4:
    """GPT-4 via OpenRouter — OpenAI-compatible params."""
    sampling: _OR_GPT4_Sampling
    length: _OR_GPT4_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "sampling", _OR_GPT4_Sampling())
        object.__setattr__(self, "length", _OR_GPT4_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_OpenRouter(), _M_GPT4()))


# -- o-series --

class _OR_O_REASONING:
    """OpenRouter: o-series reasoning — OpenAI-style reasoning effort."""
    def __init__(self) -> None:
        object.__setattr__(self, "none", PresetDict({"reasoning": {"effort": "none"}}))
        object.__setattr__(self, "low", PresetDict({"reasoning": {"effort": "low"}}))
        object.__setattr__(self, "medium", PresetDict({"reasoning": {"effort": "medium"}}))
        object.__setattr__(self, "high", PresetDict({"reasoning": {"effort": "high"}}))


class _OR_O_Length(_OR_QWEN3_6_Length):
    pass


class _OR_OSERIES:
    """o-series via OpenRouter — OpenAI-compatible params."""
    reasoning: _OR_O_REASONING
    length: _OR_O_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "reasoning", _OR_O_REASONING())
        object.__setattr__(self, "length", _OR_O_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_OpenRouter(), _M_OSERIES()))


# -- Gemini --

class _OR_GEMINI_Thinking:
    """OpenRouter: Gemini thinking — normalised."""
    def __init__(self) -> None:
        object.__setattr__(self, "disabled", PresetDict({"google_thinking_config": {"disable": True}}))
        object.__setattr__(self, "low", PresetDict({"google_thinking_config": {"thinking_budget": {"min_tokens": 1024}}}))
        object.__setattr__(self, "medium", PresetDict({"google_thinking_config": {"thinking_budget": {"min_tokens": 4096}}}))
        object.__setattr__(self, "high", PresetDict({"google_thinking_config": {"thinking_budget": {"min_tokens": 8192}}}))


class _OR_GEMINI_Sampling:
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "general", PresetDict({"temperature": 1.0, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "coding", PresetDict({"temperature": 0.6, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50, "top_k": 10}))


class _OR_GEMINI_Length(_OR_QWEN3_6_Length):
    pass


class _OR_GEMINI:
    """Gemini via OpenRouter — OpenAI-compatible params."""
    thinking: _OR_GEMINI_Thinking
    sampling: _OR_GEMINI_Sampling
    length: _OR_GEMINI_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _OR_GEMINI_Thinking())
        object.__setattr__(self, "sampling", _OR_GEMINI_Sampling())
        object.__setattr__(self, "length", _OR_GEMINI_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_OpenRouter(), _M_GEMINI()))


# -- OpenRouter backend --

class _OpenRouter:
    """Presets for OpenRouter API."""
    qwen3_6: _OR_QWEN3_6
    llama: _OR_LLAMA
    mistral: _OR_MISTRAL
    claude: _OR_CLAUDE
    gpt4: _OR_GPT4
    o_series: _OR_OSERIES
    gemini: _OR_GEMINI

    def __init__(self) -> None:
        object.__setattr__(self, "qwen3_6", _OR_QWEN3_6())
        object.__setattr__(self, "llama", _OR_LLAMA())
        object.__setattr__(self, "mistral", _OR_MISTRAL())
        object.__setattr__(self, "claude", _OR_CLAUDE())
        object.__setattr__(self, "gpt4", _OR_GPT4())
        object.__setattr__(self, "o_series", _OR_OSERIES())
        object.__setattr__(self, "gemini", _OR_GEMINI())


openrouter = _OpenRouter()
