"""Scaleway presets — vLLM-compatible + Scaleway-specific extensions."""

from __future__ import annotations

from openhosta.presets._capabilities import (
    _IntersectionCaps, _B_Scaleway, _M_QWEN3_6, _M_LLAMA, _M_CLAUDE,
)
from openhosta.presets import PresetDict
from openhosta.presets._vllm import (
    _VL_QWEN3_6_Thinking, _VL_QWEN3_6_Sampling, _VL_QWEN3_6_Length, _VL_QWEN3_6_Safety,
    _VL_LLAMA_Sampling, _VL_LLAMA_Length,
    _VL_CLAUDE_Thinking, _VL_CLAUDE_Sampling, _VL_CLAUDE_Length,
)


# -- Qwen 3.6 --

class _SW_QWEN3_6_Thinking(_VL_QWEN3_6_Thinking):
    """Scaleway: Qwen 3.6 thinking — inherits vLLM params."""
    def __init__(self) -> None:
        super().__init__()
        # Scaleway-specific extension: accelerated thinking with GPU cache
        object.__setattr__(self, "sw_accelerated", PresetDict({
            "chat_template_kwargs": {"enable_thinking": True},
            "x_scaleway_cache": True,
        }))


class _SW_QWEN3_6_Sampling(_VL_QWEN3_6_Sampling):
    """Scaleway: Qwen 3.6 sampling — inherits vLLM params."""
    pass


class _SW_QWEN3_6_Length(_VL_QWEN3_6_Length):
    """Scaleway: Qwen 3.6 length — inherits vLLM params."""
    pass


class _SW_QWEN3_6_Safety(_VL_QWEN3_6_Safety):
    """Scaleway: Qwen 3.6 safety — inherits vLLM params."""
    pass


class _SW_QWEN3_6:
    """Qwen 3.6 model presets for Scaleway ML.

    Inherits all vLLM.qwen3_6 presets, plus Scaleway-specific extensions.

    Examples:
        scaleway.qwen3_6.thinking.disabled | scaleway.qwen3_6.sampling.coding
        scaleway.qwen3_6.thinking.sw_accelerated   # Scaleway-specific
    """
    thinking: _SW_QWEN3_6_Thinking
    sampling: _SW_QWEN3_6_Sampling
    length: _SW_QWEN3_6_Length
    safety: _SW_QWEN3_6_Safety
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _SW_QWEN3_6_Thinking())
        object.__setattr__(self, "sampling", _SW_QWEN3_6_Sampling())
        object.__setattr__(self, "length", _SW_QWEN3_6_Length())
        object.__setattr__(self, "safety", _SW_QWEN3_6_Safety())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_Scaleway(), _M_QWEN3_6()))


# -- Llama --

class _SW_LLAMA_Sampling(_VL_LLAMA_Sampling):
    """Scaleway: Llama sampling — inherits vLLM params."""
    pass


class _SW_LLAMA_Length(_VL_LLAMA_Length):
    """Scaleway: Llama length — inherits vLLM params."""
    pass


class _SW_LLAMA_Safety(_VL_QWEN3_6_Safety):
    """Scaleway: Llama safety — inherits vLLM params."""
    pass


class _SW_LLAMA:
    thinking: _SW_QWEN3_6_Thinking
    sampling: _SW_LLAMA_Sampling
    length: _SW_LLAMA_Length
    safety: _SW_LLAMA_Safety
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _SW_QWEN3_6_Thinking())
        object.__setattr__(self, "sampling", _SW_LLAMA_Sampling())
        object.__setattr__(self, "length", _SW_LLAMA_Length())
        object.__setattr__(self, "safety", _SW_LLAMA_Safety())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_Scaleway(), _M_LLAMA()))


# -- Claude --

class _SW_CLAUDE_Thinking(_VL_CLAUDE_Thinking):
    """Scaleway: Claude thinking — inherits vLLM params."""
    pass


class _SW_CLAUDE_Sampling(_VL_CLAUDE_Sampling):
    """Scaleway: Claude sampling — inherits vLLM params."""
    pass


class _SW_CLAUDE_Length(_VL_CLAUDE_Length):
    """Scaleway: Claude length — inherits vLLM params."""
    pass


class _SW_CLAUDE:
    thinking: _SW_CLAUDE_Thinking
    sampling: _SW_CLAUDE_Sampling
    length: _SW_CLAUDE_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _SW_CLAUDE_Thinking())
        object.__setattr__(self, "sampling", _SW_CLAUDE_Sampling())
        object.__setattr__(self, "length", _SW_CLAUDE_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_Scaleway(), _M_CLAUDE()))


# -- Scaleway backend --

class _Scaleway:
    """Presets for Scaleway ML backend (vLLM-compatible + SW extensions)."""
    qwen3_6: _SW_QWEN3_6
    llama: _SW_LLAMA
    claude: _SW_CLAUDE

    def __init__(self) -> None:
        object.__setattr__(self, "qwen3_6", _SW_QWEN3_6())
        object.__setattr__(self, "llama", _SW_LLAMA())
        object.__setattr__(self, "claude", _SW_CLAUDE())


scaleway = _Scaleway()
