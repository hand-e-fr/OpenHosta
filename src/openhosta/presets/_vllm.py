"""vLLM presets — reference backend for most self-hosted models."""

from __future__ import annotations

from openhosta.presets._capabilities import (
    _Caps, _IntersectionCaps,
    _B_VLLM, _M_QWEN3_6, _M_LLAMA, _M_MISTRAL, _M_CLAUDE,
)
from openhosta.presets import PresetDict


# -- Qwen 3.6 --

class _VL_QWEN3_6_Thinking:
    """vLLM: Qwen 3.6 thinking/reasoning mode.

    Equivalent to:
    - SGLang: same params
    - OpenAI o-series: ``reasoning.effort``
    - Anthropic: ``thinking: {type, budget_tokens}``
    - Gemini: ``thinking_config: {budget}

    Examples:
        vllm.qwen3_6.thinking.disabled   # → enable_thinking: False
        vllm.qwen3_6.thinking.enabled     → enable_thinking: True
        vllm.qwen3_6.thinking.preserve    # → preserve_thinking: True
    """

    def __init__(self) -> None:
        object.__setattr__(self, "disabled", PresetDict({"chat_template_kwargs": {"enable_thinking": False}}))
        object.__setattr__(self, "enabled", PresetDict({"chat_template_kwargs": {"enable_thinking": True}}))
        object.__setattr__(self, "preserve", PresetDict({"chat_template_kwargs": {"preserve_thinking": True}}))


class _VL_QWEN3_6_Sampling:
    """vLLM: Qwen 3.6 sampling parameters.

    Equivalent presets exist on all backends with identical temperature/top_p/top_k values.
    See ``_base.py`` for the cross-backend equivalence table.

    Examples:
        vllm.qwen3_6.sampling.creative   # → temp=1.0, top_p=0.95, top_k=20
        vllm.qwen3_6.sampling.coding     # → temp=0.6, top_p=0.95, top_k=20
        vllm.qwen3_6.sampling.precise    # → temp=0.2, top_p=0.50, top_k=10, rep_pen=1.1
    """

    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "general", PresetDict({"temperature": 1.0, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "coding", PresetDict({"temperature": 0.6, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "instruct", PresetDict({"temperature": 0.7, "top_p": 0.80, "top_k": 20, "presence_penalty": 1.5}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50, "top_k": 10, "repetition_penalty": 1.1}))


class _VL_QWEN3_6_Length:
    """vLLM: Qwen 3.6 output length. Equivalent to ``max_tokens`` on all backends."""

    def __init__(self) -> None:
        object.__setattr__(self, "short", PresetDict({"max_tokens": 256}))
        object.__setattr__(self, "medium", PresetDict({"max_tokens": 2048}))
        object.__setattr__(self, "long", PresetDict({"max_tokens": 8192}))


class _VL_QWEN3_6_Safety:
    """vLLM: Qwen 3.6 content filtering preset via penalty parameters.

    Equivalent on other backends:
    - Anthropic: ``safety: {level}``
    - OpenAI / Gemini: content filter settings
    """

    def __init__(self) -> None:
        object.__setattr__(self, "strict", PresetDict({"presence_penalty": 2.0}))
        object.__setattr__(self, "relaxed", PresetDict({"presence_penalty": 0.0}))
        object.__setattr__(self, "off", PresetDict({"frequency_penalty": 0.0, "presence_penalty": 0.0}))


class _VL_QWEN3_6:
    """Qwen 3.6 model presets for vLLM.

    Examples:
        vllm.qwen3_6.thinking.disabled | vllm.qwen3_6.sampling.coding
        vllm.qwen3_6.sampling.creative | vllm.qwen3_6.length.long

    Attributes:
        capabilities: vLLM ∩ Qwen3.6 feature support.
    """

    thinking: _VL_QWEN3_6_Thinking
    sampling: _VL_QWEN3_6_Sampling
    length: _VL_QWEN3_6_Length
    safety: _VL_QWEN3_6_Safety
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _VL_QWEN3_6_Thinking())
        object.__setattr__(self, "sampling", _VL_QWEN3_6_Sampling())
        object.__setattr__(self, "length", _VL_QWEN3_6_Length())
        object.__setattr__(self, "safety", _VL_QWEN3_6_Safety())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_VLLM(), _M_QWEN3_6()))


# -- Llama --

class _VL_LLAMA_Sampling:
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95, "top_k": 50}))
        object.__setattr__(self, "general", PresetDict({"temperature": 0.8, "top_p": 0.95, "top_k": 50}))
        object.__setattr__(self, "coding", PresetDict({"temperature": 0.6, "top_p": 0.95, "top_k": 20}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50, "top_k": 10}))


class _VL_LLAMA_Length(_VL_QWEN3_6_Length):
    """Llama: output length presets."""


class _VL_LLAMA_Safety(_VL_QWEN3_6_Safety):
    """Llama: output length presets."""


class _VL_LLAMA:
    thinking: _VL_QWEN3_6_Thinking
    sampling: _VL_LLAMA_Sampling
    length: _VL_LLAMA_Length
    safety: _VL_LLAMA_Safety
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _VL_QWEN3_6_Thinking())
        object.__setattr__(self, "sampling", _VL_LLAMA_Sampling())
        object.__setattr__(self, "length", _VL_LLAMA_Length())
        object.__setattr__(self, "safety", _VL_LLAMA_Safety())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_VLLM(), _M_LLAMA()))


# -- Mistral --

class _VL_MISTRAL_Sampling:
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95}))
        object.__setattr__(self, "general", PresetDict({"temperature": 0.7, "top_p": 0.9}))
        object.__setattr__(self, "coding", PresetDict({"temperature": 0.6, "top_p": 0.95}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50}))


class _VL_MISTRAL_Length(_VL_QWEN3_6_Length):
    """Mistral: output length presets."""


class _VL_MISTRAL:
    sampling: _VL_MISTRAL_Sampling
    length: _VL_MISTRAL_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "sampling", _VL_MISTRAL_Sampling())
        object.__setattr__(self, "length", _VL_MISTRAL_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_VLLM(), _M_MISTRAL()))


# -- Claude (self-hosted via vLLM) --

class _VL_CLAUDE_Thinking:
    """vLLM: Claude thinking (self-hosted via vLLM).

    Equivalent to anthropic.claude.thinking with different param names.
    """

    def __init__(self) -> None:
        object.__setattr__(self, "disabled", PresetDict({"chat_template_kwargs": {"enable_thinking": False}}))
        object.__setattr__(self, "enabled", PresetDict({"chat_template_kwargs": {"enable_thinking": True}}))
        object.__setattr__(self, "minimal", PresetDict({"chat_template_kwargs": {"thinking_budget_tokens": 128}}))
        object.__setattr__(self, "low", PresetDict({"chat_template_kwargs": {"thinking_budget_tokens": 1024}}))
        object.__setattr__(self, "medium", PresetDict({"chat_template_kwargs": {"thinking_budget_tokens": 4096}}))
        object.__setattr__(self, "high", PresetDict({"chat_template_kwargs": {"thinking_budget_tokens": 8192}}))
        object.__setattr__(self, "max", PresetDict({"chat_template_kwargs": {"thinking_budget_tokens": 16384}}))


class _VL_CLAUDE_Sampling:
    def __init__(self) -> None:
        object.__setattr__(self, "creative", PresetDict({"temperature": 1.0, "top_p": 0.95}))
        object.__setattr__(self, "precise", PresetDict({"temperature": 0.2, "top_p": 0.50}))


class _VL_CLAUDE_Length(_VL_QWEN3_6_Length):
    """Claude via vLLM: output length presets."""


class _VL_CLAUDE:
    """Claude via vLLM (self-hosted).

    Equivalent to anthropic.claude but with vLLM params.
    """

    thinking: _VL_CLAUDE_Thinking
    sampling: _VL_CLAUDE_Sampling
    length: _VL_CLAUDE_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _VL_CLAUDE_Thinking())
        object.__setattr__(self, "sampling", _VL_CLAUDE_Sampling())
        object.__setattr__(self, "length", _VL_CLAUDE_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_VLLM(), _M_CLAUDE()))


# -- vLLM backend --

class _VLLM:
    """Presets for the vLLM inference backend.

    Examples:
        from openhosta.presets import vllm
        body = vllm.qwen3_6.thinking.disabled | vllm.qwen3_6.sampling.coding
    """

    qwen3_6: _VL_QWEN3_6
    llama: _VL_LLAMA
    mistral: _VL_MISTRAL
    claude: _VL_CLAUDE

    def __init__(self) -> None:
        object.__setattr__(self, "qwen3_6", _VL_QWEN3_6())
        object.__setattr__(self, "llama", _VL_LLAMA())
        object.__setattr__(self, "mistral", _VL_MISTRAL())
        object.__setattr__(self, "claude", _VL_CLAUDE())


vllm = _VLLM()
