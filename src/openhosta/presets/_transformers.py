"""Transformers presets — HF local inference (no native thinking, limited tooling)."""

from __future__ import annotations

from openhosta.presets._capabilities import (
    _IntersectionCaps, _B_Transformers, _M_QWEN3_6, _M_LLAMA, _M_CLAUDE,
)
from openhosta.presets import PresetDict


# -- Qwen 3.6 --

class _TF_QWEN3_6_Sampling:
    """Transformers: Qwen 3.6 sampling — HF params (no top_k, no repetition_penalty natively)."""
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95}))
        object.__setattr__(self, "general", PresetDict({"temperature": 1.0, "top_p": 0.95}))
        object.__setattr__(self, "coding", PresetDict({"temperature": 0.6, "top_p": 0.95}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50}))


class _TF_QWEN3_6_Length:
    def __init__(self) -> None:
        object.__setattr__(self, "short", PresetDict({"max_tokens": 256}))
        object.__setattr__(self, "medium", PresetDict({"max_tokens": 2048}))
        object.__setattr__(self, "long", PresetDict({"max_tokens": 8192}))


class _TF_QWEN3_6:
    """Qwen 3.6 via Transformers — no thinking (model only, no server)."""
    sampling: _TF_QWEN3_6_Sampling
    length: _TF_QWEN3_6_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "sampling", _TF_QWEN3_6_Sampling())
        object.__setattr__(self, "length", _TF_QWEN3_6_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_Transformers(), _M_QWEN3_6()))


# -- Llama --

class _TF_LLAMA_Sampling(_TF_QWEN3_6_Sampling):
    """Transformers: Llama sampling."""
    pass


class _TF_LLAMA_Length(_TF_QWEN3_6_Length):
    """Transformers: Llama length."""
    pass


class _TF_LLAMA:
    sampling: _TF_LLAMA_Sampling
    length: _TF_LLAMA_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "sampling", _TF_LLAMA_Sampling())
        object.__setattr__(self, "length", _TF_LLAMA_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_Transformers(), _M_LLAMA()))


# -- Claude --

class _TF_CLAUDE_Sampling(_TF_QWEN3_6_Sampling):
    """Transformers: Claude sampling."""
    pass


class _TF_CLAUDE_Length(_TF_QWEN3_6_Length):
    """Transformers: Claude length."""
    pass


class _TF_CLAUDE:
    sampling: _TF_CLAUDE_Sampling
    length: _TF_CLAUDE_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "sampling", _TF_CLAUDE_Sampling())
        object.__setattr__(self, "length", _TF_CLAUDE_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_Transformers(), _M_CLAUDE()))


# -- Transformers backend --

class _Transformers:
    """Presets for HuggingFace Transformers backend."""
    qwen3_6: _TF_QWEN3_6
    llama: _TF_LLAMA
    claude: _TF_CLAUDE

    def __init__(self) -> None:
        object.__setattr__(self, "qwen3_6", _TF_QWEN3_6())
        object.__setattr__(self, "llama", _TF_LLAMA())
        object.__setattr__(self, "claude", _TF_CLAUDE())


transformers = _Transformers()
