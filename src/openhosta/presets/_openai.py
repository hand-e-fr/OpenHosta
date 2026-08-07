"""OpenAI presets — native API (gpt-4, o-series)."""

from __future__ import annotations

from openhosta.presets._capabilities import (
    _IntersectionCaps, _B_OpenAI, _B_OpenAI_O, _M_GPT4, _M_OSERIES, _M_CLAUDE,
)
from openhosta.presets import PresetDict


# -- GPT-4 --

class _OA_GPT4_Sampling:
    """OpenAI: GPT-4 sampling — standard temp/top_p."""
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95}))
        object.__setattr__(self, "general", PresetDict({"temperature": 1.0, "top_p": 0.95}))
        object.__setattr__(self, "coding", PresetDict({"temperature": 0.6, "top_p": 0.95}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50}))


class _OA_GPT4_Length:
    def __init__(self) -> None:
        object.__setattr__(self, "short", PresetDict({"max_tokens": 256}))
        object.__setattr__(self, "medium", PresetDict({"max_tokens": 2048}))
        object.__setattr__(self, "long", PresetDict({"max_tokens": 8192}))


class _OA_GPT4_Safety:
    """OpenAI: content filter presets."""
    def __init__(self) -> None:
        object.__setattr__(self, "strict", PresetDict({"presence_penalty": 2.0}))
        object.__setattr__(self, "relaxed", PresetDict({"presence_penalty": 0.0}))
        object.__setattr__(self, "off", PresetDict({"frequency_penalty": 0.0, "presence_penalty": 0.0}))


class _OA_GPT4:
    """GPT-4 model presets for OpenAI.

    Examples:
        openai.gpt4.sampling.creative | openai.gpt4.length.long
    """
    sampling: _OA_GPT4_Sampling
    length: _OA_GPT4_Length
    safety: _OA_GPT4_Safety
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "sampling", _OA_GPT4_Sampling())
        object.__setattr__(self, "length", _OA_GPT4_Length())
        object.__setattr__(self, "safety", _OA_GPT4_Safety())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_OpenAI(), _M_GPT4()))


# -- o-series --

class _OA_O_REASONING:
    """OpenAI: o-series reasoning effort presets.

    Equivalent to thinking presets on other backends:
    - vLLM.qwen3_6.thinking.disabled → o_series.reasoning.none
    - vLLM.qwen3_6.thinking.enabled → o_series.reasoning.high
    - vLLM.qwen3_6.thinking.minimal → o_series.reasoning.low
    """
    def __init__(self) -> None:
        object.__setattr__(self, "none", PresetDict({"reasoning": {"effort": "none"}}))
        object.__setattr__(self, "low", PresetDict({"reasoning": {"effort": "low"}}))
        object.__setattr__(self, "medium", PresetDict({"reasoning": {"effort": "medium"}}))
        object.__setattr__(self, "high", PresetDict({"reasoning": {"effort": "high"}}))


class _OA_O_Sampling:
    """OpenAI: o-series sampling — limited to structured output format."""
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"response_format": {"type": "text"}}))
        object.__setattr__(self, "coding", PresetDict({"response_format": {"type": "text"}}))
        object.__setattr__(self, "precise", PresetDict({"response_format": {"type": "json_object"}}))


class _OA_O_Length:
    def __init__(self) -> None:
        object.__setattr__(self, "short", PresetDict({"max_tokens": 256}))
        object.__setattr__(self, "medium", PresetDict({"max_tokens": 2048}))
        object.__setattr__(self, "long", PresetDict({"max_tokens": 8192}))


class _OA_OSERIES:
    """OpenAI o-series model presets (o1, o3, etc.).

    Examples:
        openai.o_series.reasoning.high   # → {"reasoning": {"effort": "high"}}
        openai.o_series.reasoning.low | openai.o_series.length.medium
    """
    reasoning: _OA_O_REASONING
    sampling: _OA_O_Sampling
    length: _OA_O_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "reasoning", _OA_O_REASONING())
        object.__setattr__(self, "sampling", _OA_O_Sampling())
        object.__setattr__(self, "length", _OA_O_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_OpenAI_O(), _M_OSERIES()))


# -- Claude via OpenAI-compatible wrapper --

class _OA_CLAUDE_Thinking:
    """OpenAI-wrapper: Claude thinking (if proxy supports thinking param)."""
    def __init__(self) -> None:
        object.__setattr__(self, "disabled", PresetDict({"thinking": None}))
        object.__setattr__(self, "minimal", PresetDict({"thinking": {"type": "enabled", "budget_tokens": 128}}))
        object.__setattr__(self, "low", PresetDict({"thinking": {"type": "enabled", "budget_tokens": 1024}}))
        object.__setattr__(self, "medium", PresetDict({"thinking": {"type": "enabled", "budget_tokens": 4096}}))
        object.__setattr__(self, "high", PresetDict({"thinking": {"type": "enabled", "budget_tokens": 8192}}))
        object.__setattr__(self, "max", PresetDict({"thinking": {"type": "enabled", "budget_tokens": 16384}}))


class _OA_CLAUDE_Sampling:
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50}))


class _OA_CLAUDE:
    """Claude via OpenAI-compatible proxy."""
    thinking: _OA_CLAUDE_Thinking
    sampling: _OA_CLAUDE_Sampling
    length: _OA_GPT4_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _OA_CLAUDE_Thinking())
        object.__setattr__(self, "sampling", _OA_CLAUDE_Sampling())
        object.__setattr__(self, "length", _OA_GPT4_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_OpenAI(), _M_CLAUDE()))


# -- OpenAI backend --

class _OpenAI:
    """Presets for OpenAI backend."""
    gpt4: _OA_GPT4
    o_series: _OA_OSERIES
    claude: _OA_CLAUDE

    def __init__(self) -> None:
        object.__setattr__(self, "gpt4", _OA_GPT4())
        object.__setattr__(self, "o_series", _OA_OSERIES())
        object.__setattr__(self, "claude", _OA_CLAUDE())


openai = _OpenAI()
