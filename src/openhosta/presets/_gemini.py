"""Gemini presets — Google Gemini API."""

from __future__ import annotations

from openhosta.presets._capabilities import (
    _IntersectionCaps, _B_Gemini, _M_GEMINI, _M_GPT4, _M_CLAUDE,
)
from openhosta.presets import PresetDict


# -- Gemini --

class _GM_GEMINI_Thinking:
    """Gemini: thinking via ``thinking_config``.

    Equivalent to:
    - vLLM.qwen3_6.thinking.disabled → thinking_config: {disable: true}
    - vLLM.qwen3_6.thinking.enabled → (default model thinking)
    - anthropic.claude.thinking.medium → thinking_config: {budget: 4096}
    """
    def __init__(self) -> None:
        object.__setattr__(self, "disabled", PresetDict({"thinking_config": {"thinking_budget": {"min_tokens": 0}}}))
        object.__setattr__(self, "enabled", PresetDict({"thinking_config": {}}))
        object.__setattr__(self, "minimal", PresetDict({"thinking_config": {"thinking_budget": {"min_tokens": 128}}}))
        object.__setattr__(self, "low", PresetDict({"thinking_config": {"thinking_budget": {"min_tokens": 1024}}}))
        object.__setattr__(self, "medium", PresetDict({"thinking_config": {"thinking_budget": {"min_tokens": 4096}}}))
        object.__setattr__(self, "high", PresetDict({"thinking_config": {"thinking_budget": {"min_tokens": 8192}}}))


class _GM_GEMINI_Sampling:
    """Gemini: sampling via ``temperature`` / ``top_p`` / ``top_k``."""
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "general", PresetDict({"temperature": 1.0, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "coding", PresetDict({"temperature": 0.6, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50, "top_k": 10}))


class _GM_GEMINI_Length:
    def __init__(self) -> None:
        object.__setattr__(self, "short", PresetDict({"max_tokens": 256}))
        object.__setattr__(self, "medium", PresetDict({"max_tokens": 2048}))
        object.__setattr__(self, "long", PresetDict({"max_tokens": 8192}))


class _GM_GEMINI_Safety:
    """Gemini: content safety presets via ``safety_settings``."""
    def __init__(self) -> None:
        object.__setattr__(self, "strict", PresetDict({"safety_settings": [{"category": "HARM_CATEGORY_UNSPECIFIED", "threshold": "BLOCK_LOW_AND_ABOVE"}]}))
        object.__setattr__(self, "relaxed", PresetDict({"safety_settings": [{"category": "HARM_CATEGORY_UNSPECIFIED", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}]}))
        object.__setattr__(self, "off", PresetDict({"safety_settings": [{"category": "HARM_CATEGORY_UNSPECIFIED", "threshold": "BLOCK_NONE"}]}))


class _GM_GEMINI:
    """Gemini model presets for Google Gemini API.

    Examples:
        gemini.gemini.thinking.disabled | gemini.gemini.sampling.coding
        gemini.gemini.thinking.medium | gemini.gemini.length.long
    """
    thinking: _GM_GEMINI_Thinking
    sampling: _GM_GEMINI_Sampling
    length: _GM_GEMINI_Length
    safety: _GM_GEMINI_Safety
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _GM_GEMINI_Thinking())
        object.__setattr__(self, "sampling", _GM_GEMINI_Sampling())
        object.__setattr__(self, "length", _GM_GEMINI_Length())
        object.__setattr__(self, "safety", _GM_GEMINI_Safety())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_Gemini(), _M_GEMINI()))


# -- GPT-4 via Gemini-compatible proxy --

class _GM_GPT4_Sampling(_GM_GEMINI_Sampling):
    """Gemini-proxy: GPT-4 sampling — same params."""
    pass


class _GM_GPT4_Length(_GM_GEMINI_Length):
    """Gemini-proxy: GPT-4 length — same params."""
    pass


class _GM_GPT4:
    """GPT-4 via Gemini-compatible proxy."""
    sampling: _GM_GPT4_Sampling
    length: _GM_GPT4_Length
    safety: _GM_GEMINI_Safety
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "sampling", _GM_GPT4_Sampling())
        object.__setattr__(self, "length", _GM_GPT4_Length())
        object.__setattr__(self, "safety", _GM_GEMINI_Safety())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_Gemini(), _M_GPT4()))


# -- Claude via Gemini-compatible proxy --

class _GM_CLAUDE_Thinking(_GM_GEMINI_Thinking):
    """Gemini-proxy: Claude thinking — uses thinking_config param."""
    pass


class _GM_CLAUDE_Sampling(_GM_GEMINI_Sampling):
    """Gemini-proxy: Claude sampling."""
    pass


class _GM_CLAUDE_Length(_GM_GEMINI_Length):
    """Gemini-proxy: Claude length."""
    pass


class _GM_CLAUDE:
    """Claude via Gemini-compatible proxy."""
    thinking: _GM_CLAUDE_Thinking
    sampling: _GM_CLAUDE_Sampling
    length: _GM_CLAUDE_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _GM_CLAUDE_Thinking())
        object.__setattr__(self, "sampling", _GM_CLAUDE_Sampling())
        object.__setattr__(self, "length", _GM_CLAUDE_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_Gemini(), _M_CLAUDE()))


# -- Gemini backend --

class _Gemini:
    """Presets for Google Gemini API."""
    gemini: _GM_GEMINI
    gpt4: _GM_GPT4
    claude: _GM_CLAUDE

    def __init__(self) -> None:
        object.__setattr__(self, "gemini", _GM_GEMINI())
        object.__setattr__(self, "gpt4", _GM_GPT4())
        object.__setattr__(self, "claude", _GM_CLAUDE())


gemini = _Gemini()
