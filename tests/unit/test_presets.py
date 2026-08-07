"""Unit tests for presets module — PresetDict, capabilities, chaining."""

from __future__ import annotations

import pytest

from openhosta.presets import (
    vllm, sglang, openai, anthropic, gemini, litellm, openrouter,
    scaleway, transformers, ollama, PresetDict,
    _Caps, _IntersectionCaps,
    _M_QWEN3_6, _M_LLAMA, _M_MISTRAL, _M_CLAUDE, _M_GPT4, _M_OSERIES, _M_GEMINI,
    _B_VLLM, _B_SGLang, _B_Transformers, _B_Ollama,
    _B_OpenAI, _B_OpenAI_O, _B_Anthro, _B_Gemini,
    _B_LiteLLM, _B_OpenRouter, _B_Scaleway,
)


class TestPresetDictChaining:
    """Test PresetDict | and |= operators."""

    def test_or_returns_presdict(self) -> None:
        a = PresetDict({"a": 1})
        b = PresetDict({"b": 2})
        c = a | b
        assert isinstance(c, PresetDict)
        assert c == {"a": 1, "b": 2}

    def test_or_preserves_left(self) -> None:
        a = PresetDict({"a": 1})
        b = PresetDict({"b": 2})
        _ = a | b
        assert a == {"a": 1}

    def test_or_override(self) -> None:
        a = PresetDict({"a": 1, "b": 2})
        b = PresetDict({"b": 3})
        c = a | b
        assert c["b"] == 3

    def test_ror_with_plain_dict(self) -> None:
        a = {"a": 1}
        b = PresetDict({"b": 2})
        c = a | b
        assert isinstance(c, PresetDict)
        assert c == {"a": 1, "b": 2}

    def test_ior_modifies_self(self) -> None:
        a = PresetDict({"a": 1})
        b = PresetDict({"b": 2})
        a |= b
        assert a == {"a": 1, "b": 2}

    def test_chain_three_presets(self) -> None:
        a = PresetDict({"a": 1})
        b = PresetDict({"b": 2})
        c = PresetDict({"c": 3})
        d = a | b | c
        assert d == {"a": 1, "b": 2, "c": 3}


class TestVLLMPresets:
    """Test vLLM presets for Qwen 3.6, Llama, Mistral, Claude."""

    def test_qwen3_6_thinking_disabled(self) -> None:
        p = vllm.qwen3_6.thinking.disabled
        assert p["chat_template_kwargs"]["enable_thinking"] is False

    def test_qwen3_6_thinking_enabled(self) -> None:
        p = vllm.qwen3_6.thinking.enabled
        assert p["chat_template_kwargs"]["enable_thinking"] is True

    def test_qwen3_6_thinking_preserve(self) -> None:
        p = vllm.qwen3_6.thinking.preserve
        assert p["chat_template_kwargs"]["preserve_thinking"] is True

    def test_qwen3_6_sampling_creative(self) -> None:
        p = vllm.qwen3_6.sampling.creative
        assert p["temperature"] == 1.0
        assert p["top_p"] == 0.95
        assert p["top_k"] == 20

    def test_qwen3_6_sampling_coding(self) -> None:
        p = vllm.qwen3_6.sampling.coding
        assert p["temperature"] == 0.6

    def test_qwen3_6_sampling_precise(self) -> None:
        p = vllm.qwen3_6.sampling.precise
        assert p["temperature"] == 0.2
        assert p["top_p"] == 0.50
        assert p["repetition_penalty"] == 1.1

    def test_qwen3_6_length(self) -> None:
        assert vllm.qwen3_6.length.short["max_tokens"] == 256
        assert vllm.qwen3_6.length.medium["max_tokens"] == 2048
        assert vllm.qwen3_6.length.long["max_tokens"] == 8192

    def test_qwen3_6_chained(self) -> None:
        body = vllm.qwen3_6.thinking.disabled | vllm.qwen3_6.sampling.coding
        assert body["chat_template_kwargs"]["enable_thinking"] is False
        assert body["temperature"] == 0.6

    def test_claude_thinking_disabled(self) -> None:
        p = vllm.claude.thinking.disabled
        assert p["chat_template_kwargs"]["enable_thinking"] is False

    def test_claude_thinking_max(self) -> None:
        p = vllm.claude.thinking.max
        assert p["chat_template_kwargs"]["thinking_budget_tokens"] == 16384


class TestSGLangPresets:
    """Test SGLang presets inherit vLLM values."""

    def test_qwen3_6_thinking_same_as_vllm(self) -> None:
        assert sglang.qwen3_6.thinking.disabled == vllm.qwen3_6.thinking.disabled

    def test_qwen3_6_sampling_same_as_vllm(self) -> None:
        assert sglang.qwen3_6.sampling.coding == vllm.qwen3_6.sampling.coding

    def test_qwen3_6_length_same_as_vllm(self) -> None:
        assert sglang.qwen3_6.length.short == vllm.qwen3_6.length.short

    def test_claude_thinking_same_as_vllm(self) -> None:
        assert sglang.claude.thinking.minimal == vllm.claude.thinking.minimal


class TestTransformersPresets:
    """Test Transformers presets."""

    def test_qwen3_6_sampling_no_top_k(self) -> None:
        p = transformers.qwen3_6.sampling.creative
        assert "top_k" not in p
        assert p["temperature"] == 1.0

    def test_no_thinking_attribute(self) -> None:
        assert not hasattr(transformers.qwen3_6, "thinking")


class TestOllamaPresets:
    """Test Ollama presets."""

    def test_qwen3_6_thinking_disabled(self) -> None:
        p = ollama.qwen3_6.thinking.disabled
        assert p["thinking_enabled"] is False

    def test_qwen3_6_thinking_max(self) -> None:
        p = ollama.qwen3_6.thinking.max
        assert p["thinking_enabled"] is True
        assert p["thinking_budget_tokens"] == 16384


class TestOpenAIPresets:
    """Test OpenAI presets."""

    def test_gpt4_sampling_creative(self) -> None:
        p = openai.gpt4.sampling.creative
        assert p["temperature"] == 1.0
        assert p["top_p"] == 0.95

    def test_oseries_reasoning(self) -> None:
        assert openai.o_series.reasoning.high["reasoning"]["effort"] == "high"
        assert openai.o_series.reasoning.medium["reasoning"]["effort"] == "medium"
        assert openai.o_series.reasoning.low["reasoning"]["effort"] == "low"
        assert openai.o_series.reasoning.none["reasoning"]["effort"] == "none"

    def test_oseries_length(self) -> None:
        assert openai.o_series.length.short["max_tokens"] == 256
        assert openai.o_series.length.long["max_tokens"] == 8192


class TestAnthropicPresets:
    """Test Anthropic presets."""

    def test_claude_thinking_disabled(self) -> None:
        p = anthropic.claude.thinking.disabled
        assert p["thinking"] is None

    def test_claude_thinking_levels(self) -> None:
        assert anthropic.claude.thinking.minimal["thinking"]["budget_tokens"] == 128
        assert anthropic.claude.thinking.low["thinking"]["budget_tokens"] == 1024
        assert anthropic.claude.thinking.medium["thinking"]["budget_tokens"] == 4096
        assert anthropic.claude.thinking.high["thinking"]["budget_tokens"] == 8192
        assert anthropic.claude.thinking.max["thinking"]["budget_tokens"] == 16384

    def test_claude_bedrock_min_budget(self) -> None:
        assert anthropic.claude.bedrock.low["thinking"]["budget_tokens"] == 1024

    def test_claude_safety(self) -> None:
        assert anthropic.claude.safety.strict["safety_settings"]["level"] == "strict"
        assert anthropic.claude.safety.relaxed["safety_settings"]["level"] == "relaxed"
        assert anthropic.claude.safety.off["safety_settings"]["level"] == "none"


class TestGeminiPresets:
    """Test Gemini presets."""

    def test_thinking_disabled(self) -> None:
        p = gemini.gemini.thinking.disabled
        assert "thinking_config" in p

    def test_thinking_levels(self) -> None:
        assert gemini.gemini.thinking.low["thinking_config"]["thinking_budget"]["min_tokens"] == 1024
        assert gemini.gemini.thinking.medium["thinking_config"]["thinking_budget"]["min_tokens"] == 4096

    def test_safety_thresholds(self) -> None:
        # Gemini safety uses HARM_CATEGORY_UNSPECIFIED with BLOCK levels
        p = gemini.gemini.safety.strict
        assert any(s["threshold"] == "BLOCK_LOW_AND_ABOVE" for s in p["safety_settings"])


class TestLiteLLMPresets:
    """Test LiteLLM presets (aliases)."""

    def test_qwen3_6_thinking_alias(self) -> None:
        assert litellm.qwen3_6.thinking.disabled is not None

    def test_claude_thinking_alias(self) -> None:
        p = litellm.claude.thinking.max["anthropic_thinking"]
        assert p["budget_tokens"] == 16384


class TestOpenRouterPresets:
    """Test OpenRouter presets."""

    def test_qwen3_6_thinking(self) -> None:
        p = openrouter.qwen3_6.thinking.disabled
        assert p["chat_template_kwargs"]["enable_thinking"] is False

    def test_oseries_reasoning(self) -> None:
        assert openrouter.o_series.reasoning.high["reasoning"]["effort"] == "high"

    def test_claude_thinking(self) -> None:
        p = openrouter.claude.thinking.max["thinking"]
        assert p["budget_tokens"] == 16384


class TestScalewayPresets:
    """Test Scaleway presets (inherit from vLLM + extensions)."""

    def test_inherits_vllm_thinking(self) -> None:
        assert scaleway.qwen3_6.thinking.disabled == vllm.qwen3_6.thinking.disabled

    def test_sw_accelerated_extension(self) -> None:
        p = scaleway.qwen3_6.thinking.sw_accelerated
        assert p["x_scaleway_cache"] is True
        assert p["chat_template_kwargs"]["enable_thinking"] is True

    def test_claude_inherits_vllm(self) -> None:
        assert scaleway.claude.thinking.minimal == vllm.claude.thinking.minimal


class TestCapabilities:
    """Test backend ∩ model capability intersection."""

    def test_vllm_qwen3_6_thinking_true(self) -> None:
        assert vllm.qwen3_6.capabilities.supports["thinking"] is True

    def test_vllm_qwen3_6_vision_false(self) -> None:
        """vLLM doesn't support vision at the API level, so intersection is False."""
        assert vllm.qwen3_6.capabilities.supports["vision"] is False

    def test_vllm_qwen3_6_logprobs_true(self) -> None:
        assert vllm.qwen3_6.capabilities.supports["logprobs"] is True

    def test_vllm_qwen3_6_prompt_caching_false(self) -> None:
        """vLLM doesn't support prompt caching at the API level."""
        assert vllm.qwen3_6.capabilities.supports["prompt_caching"] is False

    def test_anthropic_claude_vision_true(self) -> None:
        """Anthropic API supports vision, Claude model supports vision → True."""
        assert anthropic.claude.capabilities.supports["vision"] is True

    def test_anthropic_claude_logprobs_false(self) -> None:
        """Anthropic API doesn't support logprobs → False regardless of model."""
        assert anthropic.claude.capabilities.supports["logprobs"] is False

    def test_openai_gpt4_thinking_false(self) -> None:
        """OpenAI GPT-4 doesn't support thinking natively (temp, not thinking)."""
        assert openai.gpt4.capabilities.supports["thinking"] is False

    def test_openai_oseries_thinking_true(self) -> None:
        """OpenAI o-series supports thinking via reasoning effort."""
        assert openai.o_series.capabilities.supports["thinking"] is True

    def test_openai_oseries_tool_calling_false(self) -> None:
        """OpenAI o-series doesn't support tool calling."""
        assert openai.o_series.capabilities.supports["tool_calling"] is False

    def test_transformers_qwen3_6_no_thinking(self) -> None:
        """Transformers backend doesn't support thinking."""
        assert transformers.qwen3_6.capabilities.supports["thinking"] is False

    def test_transformers_qwen3_6_no_tool_calling(self) -> None:
        """Transformers backend doesn't support tool calling."""
        assert transformers.qwen3_6.capabilities.supports["tool_calling"] is False

    def test_ollama_qwen3_6_logprobs_false(self) -> None:
        """Ollama API doesn't support logprobs."""
        assert ollama.qwen3_6.capabilities.supports["logprobs"] is False

    def test_litellm_full_support(self) -> None:
        """LiteLLM proxy supports everything conservatively."""
        for k, v in litellm.qwen3_6.capabilities.supports.items():
            assert v is True, f"LiteLLM should support {k}"

    def test_openrouter_full_support(self) -> None:
        """OpenRouter supports everything conservatively."""
        for k, v in openrouter.qwen3_6.capabilities.supports.items():
            assert v is True, f"OpenRouter should support {k}"


class TestSamePresetNamesAcrossBackends:
    """Verify same preset names exist across self-hosted backends (semantic equivalence).

    Note: Only self-hosted backends (vllm, sglang, transformers, ollama, scaleway) and
    proxy backends (litellm, openrouter) carry Qwen 3.6 presets uniformly.
    Cloud backends (openai, anthropic, gemini) carry their own native models first."""

    _QWEN_BACKENDS = [vllm, sglang, transformers, ollama, scaleway, litellm, openrouter]

    def test_sampling_creative_exists_all(self) -> None:
        """sampling.creative should exist on all self-hosted backends for Qwen 3.6."""
        for backend in self._QWEN_BACKENDS:
            assert hasattr(backend.qwen3_6.sampling, "creative")

    def test_sampling_coding_exists_all(self) -> None:
        for backend in self._QWEN_BACKENDS:
            assert hasattr(backend.qwen3_6.sampling, "coding")

    def test_sampling_precise_exists_all(self) -> None:
        for backend in self._QWEN_BACKENDS:
            assert hasattr(backend.qwen3_6.sampling, "precise")

    def test_length_short_exists_all(self) -> None:
        for backend in self._QWEN_BACKENDS:
            assert hasattr(backend.qwen3_6.length, "short")

    def test_length_long_exists_all(self) -> None:
        for backend in self._QWEN_BACKENDS:
            assert hasattr(backend.qwen3_6.length, "long")

    def test_capabilities_exists_all(self) -> None:
        for backend in self._QWEN_BACKENDS:
            assert hasattr(backend.qwen3_6, "capabilities")

    def test_sampling_creative_same_temp(self) -> None:
        """sampling.creative should use temp=1.0 on all self-hosted backends."""
        for backend in self._QWEN_BACKENDS:
            assert backend.qwen3_6.sampling.creative["temperature"] == 1.0

    def test_sampling_coding_same_temp(self) -> None:
        """sampling.coding should use temp=0.6 on all self-hosted backends."""
        for backend in self._QWEN_BACKENDS:
            assert backend.qwen3_6.sampling.coding["temperature"] == 0.6

    def test_length_short_same_max_tokens(self) -> None:
        """length.short should use max_tokens=256 on all self-hosted backends."""
        for backend in self._QWEN_BACKENDS:
            assert backend.qwen3_6.length.short["max_tokens"] == 256

    def test_length_long_same_max_tokens(self) -> None:
        """length.long should use max_tokens=8192 on all self-hosted backends."""
        for backend in self._QWEN_BACKENDS:
            assert backend.qwen3_6.length.long["max_tokens"] == 8192


class TestCrossBackendCapabilities:
    """Test that capabilities change correctly when backend or model changes."""

    def test_vllm_no_vision_anthropic_has_vision(self) -> None:
        """vLLM ∩ Claude has no vision (backend lacks vision).
        Anthropic ∩ Claude has vision (both support it).
        """
        assert vllm.claude.capabilities.supports["vision"] is False
        assert anthropic.claude.capabilities.supports["vision"] is True

    def test_vllm_no_logprobs_for_claude(self) -> None:
        """Claude model doesn't support logprobs, so intersection is False
        regardless of backend.
        """
        assert vllm.claude.capabilities.supports["logprobs"] is False
        assert sglang.claude.capabilities.supports["logprobs"] is False

    def test_openai_gpt4_has_vision(self) -> None:
        """OpenAI GPT-4 has vision in both model and API → True."""
        assert openai.gpt4.capabilities.supports["vision"] is True

    def test_gemini_has_vision_and_audio(self) -> None:
        """Gemini model + API both support vision and audio."""
        assert gemini.gemini.capabilities.supports["vision"] is True
        assert gemini.gemini.capabilities.supports["audio"] is True


class TestModelCapabilities:
    """Test model-side capabilities are correct."""

    def test_qwen3_6_supports_thinking(self) -> None:
        assert _M_QWEN3_6().supports["thinking"] is True

    def test_llama_no_thinking(self) -> None:
        assert _M_LLAMA().supports["thinking"] is False

    def test_claude_supports_thinking(self) -> None:
        assert _M_CLAUDE().supports["thinking"] is True

    def test_gpt4_no_thinking(self) -> None:
        assert _M_GPT4().supports["thinking"] is False

    def test_oseries_supports_thinking(self) -> None:
        assert _M_OSERIES().supports["thinking"] is True

    def test_mistral_has_vision(self) -> None:
        assert _M_MISTRAL().supports["vision"] is True


class TestBackendCapabilities:
    """Test backend-side capabilities are correct."""

    def test_vllm_no_vision(self) -> None:
        assert _B_VLLM().supports["vision"] is False

    def test_vllm_has_thinking(self) -> None:
        assert _B_VLLM().supports["thinking"] is True

    def test_anthropic_no_structured_output(self) -> None:
        assert _B_Anthro().supports["structured_output"] is False

    def test_anthropic_has_thinking(self) -> None:
        assert _B_Anthro().supports["thinking"] is True

    def test_transformers_no_thinking(self) -> None:
        assert _B_Transformers().supports["thinking"] is False

    def test_ollama_no_logprobs(self) -> None:
        assert _B_Ollama().supports["logprobs"] is False

    def test_openrouter_full_support(self) -> None:
        for k, v in _B_OpenRouter().supports.items():
            assert v is True, f"OpenRouter should support {k}"


class TestUsagePatterns:
    """Test realistic usage patterns from the backend."""

    def test_body_from_vllm_qwen(self) -> None:
        """Verify body dict can be used directly with backend."""
        body = vllm.qwen3_6.thinking.disabled | vllm.qwen3_6.sampling.coding
        assert isinstance(body, dict)
        assert "chat_template_kwargs" in body
        assert "temperature" in body

    def test_body_from_anthropic_claude(self) -> None:
        """Verify body dict for Anthropic."""
        body = anthropic.claude.thinking.medium | anthropic.claude.sampling.creative
        assert isinstance(body, dict)
        assert body["thinking"]["type"] == "enabled"
        assert body["thinking"]["budget_tokens"] == 4096
        assert body["temperature"] == 1.0

    def test_body_from_openai_oseries(self) -> None:
        """Verify body dict for OpenAI o-series."""
        body = openai.o_series.reasoning.high | openai.o_series.length.long
        assert isinstance(body, dict)
        assert body["reasoning"]["effort"] == "high"
        assert body["max_tokens"] == 8192

    def test_guarded_by_capabilities(self) -> None:
        """Verify pattern: check capabilities before applying preset."""
        if vllm.qwen3_6.capabilities.supports["thinking"]:
            body = vllm.qwen3_6.thinking.disabled | vllm.qwen3_6.sampling.coding
            assert body["chat_template_kwargs"]["enable_thinking"] is False
        else:
            pytest.fail("Qwen3.6 + vLLM should support thinking")

    def test_guarded_anthropic_no_structured_output(self) -> None:
        """Verify Anthropic Claude won't suggest structured_output preset."""
        assert anthropic.claude.capabilities.supports["structured_output"] is False
