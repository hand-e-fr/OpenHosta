"""Ollama presets — OpenAI-compatible endpoint."""

from __future__ import annotations

from openhosta.presets._capabilities import (
    _IntersectionCaps, _B_Ollama, _M_QWEN3_6, _M_LLAMA, _M_MISTRAL, _M_CLAUDE,
)
from openhosta.presets import PresetDict
from openhosta.presets._vllm import (
    _VL_QWEN3_6_Thinking, _VL_QWEN3_6_Sampling, _VL_QWEN3_6_Length, _VL_CLAUDE_Thinking, _VL_CLAUDE_Sampling,
)


# -- Qwen 3.6 --

class _OL_QWEN3_6_Thinking:
    """Ollama: Qwen 3.6 thinking via ``thinking_enabled`` + ``thinking_budget_tokens``.

    Equivalent to vLLM ``chat_template_kwargs.enable_thinking``.
    """
    def __init__(self) -> None:
        object.__setattr__(self, "disabled", PresetDict({"thinking_enabled": False}))
        object.__setattr__(self, "enabled", PresetDict({"thinking_enabled": True}))
        object.__setattr__(self, "minimal", PresetDict({"thinking_enabled": True, "thinking_budget_tokens": 128}))
        object.__setattr__(self, "low", PresetDict({"thinking_enabled": True, "thinking_budget_tokens": 1024}))
        object.__setattr__(self, "medium", PresetDict({"thinking_enabled": True, "thinking_budget_tokens": 4096}))
        object.__setattr__(self, "high", PresetDict({"thinking_enabled": True, "thinking_budget_tokens": 8192}))
        object.__setattr__(self, "max", PresetDict({"thinking_enabled": True, "thinking_budget_tokens": 16384}))


class _OL_QWEN3_6_Sampling(_VL_QWEN3_6_Sampling):
    """Ollama: Qwen 3.6 sampling — identical params to vLLM."""
    pass


class _OL_QWEN3_6_Length:
    """Ollama: uses ``num_ctx`` for context window, ``max_tokens`` for output."""
    def __init__(self) -> None:
        object.__setattr__(self, "short", PresetDict({"max_tokens": 256}))
        object.__setattr__(self, "medium", PresetDict({"max_tokens": 2048}))
        object.__setattr__(self, "long", PresetDict({"max_tokens": 8192}))


class _OL_QWEN3_6_Safety:
    """Ollama: content filtering presets."""
    def __init__(self) -> None:
        object.__setattr__(self, "strict", PresetDict({"presence_penalty": 2.0}))
        object.__setattr__(self, "relaxed", PresetDict({"presence_penalty": 0.0}))
        object.__setattr__(self, "off", PresetDict({"frequency_penalty": 0.0, "presence_penalty": 0.0}))


class _OL_QWEN3_6:
    thinking: _OL_QWEN3_6_Thinking
    sampling: _OL_QWEN3_6_Sampling
    length: _OL_QWEN3_6_Length
    safety: _OL_QWEN3_6_Safety
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _OL_QWEN3_6_Thinking())
        object.__setattr__(self, "sampling", _OL_QWEN3_6_Sampling())
        object.__setattr__(self, "length", _OL_QWEN3_6_Length())
        object.__setattr__(self, "safety", _OL_QWEN3_6_Safety())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_Ollama(), _M_QWEN3_6()))


# -- Llama --

class _OL_LLAMA_Sampling:
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95, "top_k": 50}))
        object.__setattr__(self, "general", PresetDict({"temperature": 0.8, "top_p": 0.95, "top_k": 50}))
        object.__setattr__(self, "coding", PresetDict({"temperature": 0.6, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50, "top_k": 10}))


class _OL_LLAMA_Length(_OL_QWEN3_6_Length):
    """Ollama: Llama length."""
    pass


class _OL_LLAMA:
    sampling: _OL_LLAMA_Sampling
    length: _OL_LLAMA_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "sampling", _OL_LLAMA_Sampling())
        object.__setattr__(self, "length", _OL_LLAMA_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_Ollama(), _M_LLAMA()))


# -- Mistral --

class _OL_MISTRAL_Sampling:
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95}))
        object.__setattr__(self, "general", PresetDict({"temperature": 0.7, "top_p": 0.9}))
        object.__setattr__(self, "coding", PresetDict({"temperature": 0.6, "top_p": 0.95}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50}))


class _OL_MISTRAL_Length(_OL_QWEN3_6_Length):
    """Ollama: Mistral length."""
    pass


class _OL_MISTRAL:
    sampling: _OL_MISTRAL_Sampling
    length: _OL_MISTRAL_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "sampling", _OL_MISTRAL_Sampling())
        object.__setattr__(self, "length", _OL_MISTRAL_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_Ollama(), _M_MISTRAL()))


# -- Claude --

class _OL_CLAUDE_Thinking(_OL_QWEN3_6_Thinking):
    """Ollama: Claude thinking — same as Qwen 3.6 (Ollama normalises)."""
    pass


class _OL_CLAUDE_Sampling(_VL_CLAUDE_Sampling):
    """Ollama: Claude sampling."""
    pass


class _OL_CLAUDE_Length(_OL_QWEN3_6_Length):
    """Ollama: Claude length."""
    pass


class _OL_CLAUDE:
    thinking: _OL_CLAUDE_Thinking
    sampling: _OL_CLAUDE_Sampling
    length: _OL_CLAUDE_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _OL_CLAUDE_Thinking())
        object.__setattr__(self, "sampling", _OL_CLAUDE_Sampling())
        object.__setattr__(self, "length", _OL_CLAUDE_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_Ollama(), _M_CLAUDE()))


# -- Ollama backend --

class _Ollama:
    """Presets for Ollama backend (OpenAI-compatible endpoint)."""
    qwen3_6: _OL_QWEN3_6
    llama: _OL_LLAMA
    mistral: _OL_MISTRAL
    claude: _OL_CLAUDE

    def __init__(self) -> None:
        object.__setattr__(self, "qwen3_6", _OL_QWEN3_6())
        object.__setattr__(self, "llama", _OL_LLAMA())
        object.__setattr__(self, "mistral", _OL_MISTRAL())
        object.__setattr__(self, "claude", _OL_CLAUDE())


ollama = _Ollama()
