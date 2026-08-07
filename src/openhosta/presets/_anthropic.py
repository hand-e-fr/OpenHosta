"""Anthropic presets — native Messages API (claude)."""

from __future__ import annotations

from openhosta.presets._capabilities import (
    _IntersectionCaps, _B_Anthro, _M_CLAUDE, _M_QWEN3_6, _M_GEMINI,
)
from openhosta.presets import PresetDict


# -- Claude --

class _AC_CLAUDE_Thinking:
    """Anthropic: Claude thinking via ``thinking`` block.

    Equivalent to:
    - vLLM.qwen3_6.thinking.disabled → thinking: disabled (budget_tokens: 0)
    - vLLM.qwen3_6.thinking.enabled → thinking: {type: "enabled"}
    - openai.o_series.reasoning.high → thinking: {budget_tokens: 8192}

    Bedrock minimum budget_tokens is 1024 for Anthropic/Bedrock models.
    """
    def __init__(self) -> None:
        object.__setattr__(self, "disabled", PresetDict({"thinking": None}))
        object.__setattr__(self, "enabled", PresetDict({"thinking": {"type": "enabled"}}))
        object.__setattr__(self, "minimal", PresetDict({"thinking": {"type": "enabled", "budget_tokens": 128}}))
        object.__setattr__(self, "low", PresetDict({"thinking": {"type": "enabled", "budget_tokens": 1024}}))
        object.__setattr__(self, "medium", PresetDict({"thinking": {"type": "enabled", "budget_tokens": 4096}}))
        object.__setattr__(self, "high", PresetDict({"thinking": {"type": "enabled", "budget_tokens": 8192}}))
        object.__setattr__(self, "max", PresetDict({"thinking": {"type": "enabled", "budget_tokens": 16384}}))


class _AC_CLAUDE_Bedrock:
    """Anthropic on AWS Bedrock — min budget_tokens = 1024."""
    def __init__(self) -> None:
        object.__setattr__(self, "low", PresetDict({"thinking": {"type": "enabled", "budget_tokens": 1024}}))
        object.__setattr__(self, "medium", PresetDict({"thinking": {"type": "enabled", "budget_tokens": 4096}}))
        object.__setattr__(self, "high", PresetDict({"thinking": {"type": "enabled", "budget_tokens": 8192}}))
        object.__setattr__(self, "max", PresetDict({"thinking": {"type": "enabled", "budget_tokens": 16384}}))


class _AC_CLAUDE_Sampling:
    """Anthropic: Claude sampling — standard temp/top_p."""
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50}))


class _AC_CLAUDE_Length:
    """Anthropic: Claude output length via ``max_tokens``."""
    def __init__(self) -> None:
        object.__setattr__(self, "short", PresetDict({"max_tokens": 256}))
        object.__setattr__(self, "medium", PresetDict({"max_tokens": 2048}))
        object.__setattr__(self, "long", PresetDict({"max_tokens": 8192}))


class _AC_CLAUDE_Safety:
    """Anthropic: Claude safety presets via ``safety`` parameter."""
    def __init__(self) -> None:
        object.__setattr__(self, "strict", PresetDict({"safety_settings": {"level": "strict"}}))
        object.__setattr__(self, "relaxed", PresetDict({"safety_settings": {"level": "relaxed"}}))
        object.__setattr__(self, "off", PresetDict({"safety_settings": {"level": "none"}}))


class _AC_CLAUDE:
    """Claude model presets for Anthropic Messages API.

    Examples:
        anthropic.claude.thinking.disabled | anthropic.claude.sampling.creative
        anthropic.claude.thinking.medium | anthropic.claude.length.long
    """
    thinking: _AC_CLAUDE_Thinking
    bedrock: _AC_CLAUDE_Bedrock
    sampling: _AC_CLAUDE_Sampling
    length: _AC_CLAUDE_Length
    safety: _AC_CLAUDE_Safety
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _AC_CLAUDE_Thinking())
        object.__setattr__(self, "bedrock", _AC_CLAUDE_Bedrock())
        object.__setattr__(self, "sampling", _AC_CLAUDE_Sampling())
        object.__setattr__(self, "length", _AC_CLAUDE_Length())
        object.__setattr__(self, "safety", _AC_CLAUDE_Safety())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_Anthro(), _M_CLAUDE()))


# -- Qwen via Anthropic-compatible proxy --

class _AC_QWEN3_6_Thinking(_AC_CLAUDE_Thinking):
    """Anthropic-proxy: Qwen 3.6 thinking — uses thinking param."""
    pass


class _AC_QWEN3_6_Sampling(_AC_CLAUDE_Sampling):
    """Anthropic-proxy: Qwen 3.6 sampling."""
    pass


class _AC_QWEN3_6_Length(_AC_CLAUDE_Length):
    """Anthropic-proxy: Qwen 3.6 length."""
    pass


class _AC_QWEN3_6:
    """Qwen 3.6 via Anthropic-compatible proxy."""
    thinking: _AC_QWEN3_6_Thinking
    sampling: _AC_QWEN3_6_Sampling
    length: _AC_QWEN3_6_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _AC_QWEN3_6_Thinking())
        object.__setattr__(self, "sampling", _AC_QWEN3_6_Sampling())
        object.__setattr__(self, "length", _AC_QWEN3_6_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_Anthro(), _M_QWEN3_6()))


# -- Gemini via Anthropic-compatible proxy --

class _AC_GEMINI_Thinking(_AC_CLAUDE_Thinking):
    """Anthropic-proxy: Gemini thinking — uses thinking param."""
    pass


class _AC_GEMINI_Sampling(_AC_CLAUDE_Sampling):
    """Anthropic-proxy: Gemini sampling."""
    pass


class _AC_GEMINI_Length(_AC_CLAUDE_Length):
    """Anthropic-proxy: Gemini length."""
    pass


class _AC_GEMINI:
    """Gemini via Anthropic-compatible proxy."""
    thinking: _AC_GEMINI_Thinking
    sampling: _AC_GEMINI_Sampling
    length: _AC_GEMINI_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _AC_GEMINI_Thinking())
        object.__setattr__(self, "sampling", _AC_GEMINI_Sampling())
        object.__setattr__(self, "length", _AC_GEMINI_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_Anthro(), _M_GEMINI()))


# -- Anthropic backend --

class _Anthropic:
    """Presets for Anthropic Messages API."""
    claude: _AC_CLAUDE
    gemini: _AC_GEMINI

    def __init__(self) -> None:
        object.__setattr__(self, "claude", _AC_CLAUDE())
        object.__setattr__(self, "gemini", _AC_GEMINI())


anthropic = _Anthropic()
