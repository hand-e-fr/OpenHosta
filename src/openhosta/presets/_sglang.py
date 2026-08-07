"""SGLang presets — inherits vLLM params (identical API shapes)."""

from __future__ import annotations

from openhosta.presets._capabilities import (
    _Caps, _IntersectionCaps,
    _B_SGLang, _M_QWEN3_6, _M_LLAMA, _M_MISTRAL, _M_CLAUDE,
)
from openhosta.presets import PresetDict
from openhosta.presets._vllm import (
    _VL_QWEN3_6_Thinking, _VL_QWEN3_6_Sampling, _VL_QWEN3_6_Length, _VL_QWEN3_6_Safety,
    _VL_LLAMA_Sampling, _VL_LLAMA_Length,
    _VL_MISTRAL_Sampling, _VL_MISTRAL_Length,
    _VL_CLAUDE_Thinking, _VL_CLAUDE_Sampling, _VL_CLAUDE_Length,
)


# -- Qwen 3.6 --

class _SG_QWEN3_6_Thinking(_VL_QWEN3_6_Thinking):
    """SGLang: Qwen 3.6 thinking — identical params to vLLM."""


class _SG_QWEN3_6_Sampling(_VL_QWEN3_6_Sampling):
    """SGLang: Qwen 3.6 sampling — identical params to vLLM."""


class _SG_QWEN3_6_Length(_VL_QWEN3_6_Length):
    """SGLang: Qwen 3.6 length — identical params to vLLM."""


class _SG_QWEN3_6_Safety(_VL_QWEN3_6_Safety):
    """SGLang: Qwen 3.6 safety — identical params to vLLM."""


class _SG_QWEN3_6:
    """Qwen 3.6 model presets for SGLang."""

    thinking: _SG_QWEN3_6_Thinking
    sampling: _SG_QWEN3_6_Sampling
    length: _SG_QWEN3_6_Length
    safety: _SG_QWEN3_6_Safety
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _SG_QWEN3_6_Thinking())
        object.__setattr__(self, "sampling", _SG_QWEN3_6_Sampling())
        object.__setattr__(self, "length", _SG_QWEN3_6_Length())
        object.__setattr__(self, "safety", _SG_QWEN3_6_Safety())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_SGLang(), _M_QWEN3_6()))


# -- Llama --

class _SG_LLAMA_Sampling(_VL_LLAMA_Sampling):
    """SGLang: Llama sampling — identical params to vLLM."""


class _SG_LLAMA_Length(_VL_LLAMA_Length):
    """SGLang: Llama length — identical params to vLLM."""


class _SG_LLAMA_Safety(_VL_QWEN3_6_Safety):
    """SGLang: Llama safety — identical params to vLLM."""


class _SG_LLAMA:
    thinking: _SG_QWEN3_6_Thinking
    sampling: _SG_LLAMA_Sampling
    length: _SG_LLAMA_Length
    safety: _SG_LLAMA_Safety
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _SG_QWEN3_6_Thinking())
        object.__setattr__(self, "sampling", _SG_LLAMA_Sampling())
        object.__setattr__(self, "length", _SG_LLAMA_Length())
        object.__setattr__(self, "safety", _SG_LLAMA_Safety())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_SGLang(), _M_LLAMA()))


# -- Mistral --

class _SG_MISTRAL_Sampling(_VL_MISTRAL_Sampling):
    """SGLang: Mistral sampling — identical params to vLLM."""


class _SG_MISTRAL_Length(_VL_MISTRAL_Length):
    """SGLang: Mistral length — identical params to vLLM."""


class _SG_MISTRAL:
    sampling: _SG_MISTRAL_Sampling
    length: _SG_MISTRAL_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "sampling", _SG_MISTRAL_Sampling())
        object.__setattr__(self, "length", _SG_MISTRAL_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_SGLang(), _M_MISTRAL()))


# -- Claude --

class _SG_CLAUDE_Thinking(_VL_CLAUDE_Thinking):
    """SGLang: Claude thinking — identical params to vLLM."""


class _SG_CLAUDE_Sampling(_VL_CLAUDE_Sampling):
    """SGLang: Claude sampling — identical params to vLLM."""


class _SG_CLAUDE_Length(_VL_CLAUDE_Length):
    """SGLang: Claude length — identical params to vLLM."""


class _SG_CLAUDE:
    thinking: _SG_CLAUDE_Thinking
    sampling: _SG_CLAUDE_Sampling
    length: _SG_CLAUDE_Length
    capabilities: _IntersectionCaps

    def __init__(self) -> None:
        object.__setattr__(self, "thinking", _SG_CLAUDE_Thinking())
        object.__setattr__(self, "sampling", _SG_CLAUDE_Sampling())
        object.__setattr__(self, "length", _SG_CLAUDE_Length())
        object.__setattr__(self, "capabilities", _IntersectionCaps(_B_SGLang(), _M_CLAUDE()))


# -- SGLang backend --

class _SGLang:
    """Presets for the SGLang inference backend."""

    qwen3_6: _SG_QWEN3_6
    llama: _SG_LLAMA
    mistral: _SG_MISTRAL
    claude: _SG_CLAUDE

    def __init__(self) -> None:
        object.__setattr__(self, "qwen3_6", _SG_QWEN3_6())
        object.__setattr__(self, "llama", _SG_LLAMA())
        object.__setattr__(self, "mistral", _SG_MISTRAL())
        object.__setattr__(self, "claude", _SG_CLAUDE())


sglang = _SGLang()
