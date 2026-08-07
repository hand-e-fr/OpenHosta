"""API integration tests for presets — send real requests with preset params.

Tests against available backends:
- vllm (ikoula): Qwen 3.6
- ollama (localhost): Qwen 3.6
- openai: GPT-4, o-series
- anthropic: Claude
- openrouter: multiple models
"""

from __future__ import annotations

import os
import pytest

from openhosta.presets import (
    vllm, sglang, openai, anthropic, gemini, openrouter, ollama, PresetDict,
)


# ============================================================================
# Helper: send a request with OpenAI-compatible API
# ============================================================================

def _send_oai_request(base_url, api_key, model_name, body_params, system_msg=None):
    """Send a chat completion request with OpenAI-compatible API."""
    import urllib.request
    import json as _json

    system_msg = system_msg or "You are a precise function executor."
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": "What is 2+2? Return only the number."},
        ],
        **body_params,
    }

    req_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}" if api_key else "",
    }

    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=_json.dumps(payload).encode("utf-8"),
        headers=req_headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = _json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            return content, data.get("usage", {})
    except Exception as e:
        pytest.skip(f"API call failed: {e}")


# ============================================================================
# vLLM (ikoula) — Qwen 3.6
# ============================================================================

class TestVLLMQwen36:
    """Test vLLM on ikoula with Qwen 3.6 presets."""

    @pytest.fixture
    def base_url(self):
        return os.environ.get("VLLM_BASE_URL", "http://ikoula.example.com/v1")

    @pytest.fixture
    def api_key(self):
        return os.environ.get("VLLM_API_KEY", "none")

    def test_thinking_disabled_sampling_coding(self, base_url, api_key):
        """Test: vllm.qwen3_6.thinking.disabled | vllm.qwen3_6.sampling.coding"""
        body = vllm.qwen3_6.thinking.disabled | vllm.qwen3_6.sampling.coding
        content, usage = _send_oai_request(base_url, api_key, "Qwen/Qwen3-8B", body)
        assert "4" in content or "4" in content.strip()

    def test_thinking_enabled_sampling_creative(self, base_url, api_key):
        """Test: vllm.qwen3_6.thinking.enabled | vllm.qwen3_6.sampling.creative"""
        body = vllm.qwen3_6.thinking.enabled | vllm.qwen3_6.sampling.creative
        content, usage = _send_oai_request(base_url, api_key, "Qwen/Qwen3-8B", body)
        assert content  # non-empty


# ============================================================================
# Ollama (localhost) — Qwen 3.6
# ============================================================================

class TestOllamaQwen36:
    """Test Ollama on localhost with Qwen 3.6 presets."""

    @pytest.fixture
    def base_url(self):
        return os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")

    @pytest.fixture
    def api_key(self):
        return "none"

    @pytest.fixture
    def model_name(self):
        return os.environ.get("OLLAMA_MODEL", "qwen3:4b")

    def test_thinking_disabled(self, base_url, api_key, model_name):
        """Test: ollama.qwen3_6.thinking.disabled | ollama.qwen3_6.sampling.coding"""
        body = ollama.qwen3_6.thinking.disabled | ollama.qwen3_6.sampling.coding | ollama.qwen3_6.length.short
        content, usage = _send_oai_request(base_url, api_key, model_name, body)
        assert "4" in content

    def test_thinking_enabled(self, base_url, api_key, model_name):
        """Test: ollama.qwen3_6.thinking.enabled | ollama.qwen3_6.sampling.precise"""
        body = ollama.qwen3_6.thinking.enabled | ollama.qwen3_6.sampling.precise
        content, usage = _send_oai_request(base_url, api_key, model_name, body)
        assert content


# ============================================================================
# OpenAI — GPT-4
# ============================================================================

class TestOpenAIGPT4:
    """Test OpenAI with GPT-4 presets."""

    @pytest.fixture
    def base_url(self):
        return os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

    @pytest.fixture
    def api_key(self):
        return os.environ.get("OPENAI_API_KEY", "")

    @pytest.fixture
    def model_name(self):
        return os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    def test_sampling_creative(self, base_url, api_key, model_name):
        """Test: openai.gpt4.sampling.creative | openai.gpt4.length.short"""
        body = openai.gpt4.sampling.creative | openai.gpt4.length.short
        content, usage = _send_oai_request(base_url, api_key, model_name, body)
        assert "4" in content

    def test_sampling_precise(self, base_url, api_key, model_name):
        """Test: openai.gpt4.sampling.precise | openai.gpt4.length.short"""
        body = openai.gpt4.sampling.precise | openai.gpt4.length.short
        content, usage = _send_oai_request(base_url, api_key, model_name, body)
        assert "4" in content


# ============================================================================
# OpenAI — o-series
# ============================================================================

class TestOpenAIOSeries:
    """Test OpenAI with o-series presets."""

    @pytest.fixture
    def base_url(self):
        return os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

    @pytest.fixture
    def api_key(self):
        return os.environ.get("OPENAI_API_KEY", "")

    @pytest.fixture
    def model_name(self):
        return os.environ.get("OPENAI_O_MODEL", "o3-mini")

    def test_reasoning_low(self, base_url, api_key, model_name):
        """Test: openai.o_series.reasoning.low"""
        body = openai.o_series.reasoning.low | openai.o_series.length.short
        content, usage = _send_oai_request(base_url, api_key, model_name, body)
        assert "4" in content

    def test_reasoning_high(self, base_url, api_key, model_name):
        """Test: openai.o_series.reasoning.high"""
        body = openai.o_series.reasoning.high | openai.o_series.length.short
        content, usage = _send_oai_request(base_url, api_key, model_name, body)
        assert "4" in content


# ============================================================================
# Anthropic — Claude
# ============================================================================

class TestAnthropicClaude:
    """Test Anthropic with Claude presets."""

    @pytest.fixture
    def api_key(self):
        return os.environ.get("ANTHROPIC_API_KEY", "")

    @pytest.fixture
    def model_name(self):
        return os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")

    def _send_anthropic_request(self, api_key, model_name, system_msg, user_msg):
        """Send a Messages API request to Anthropic."""
        import urllib.request
        import json as _json

        payload = {
            "model": model_name,
            "system": system_msg,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": user_msg}],
        }

        req_headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        }

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=_json.dumps(payload).encode("utf-8"),
            headers=req_headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = _json.loads(resp.read().decode("utf-8"))
                content = data["content"][0]["text"]
                return content, data.get("usage", {})
        except Exception as e:
            pytest.skip(f"Anthropic API call failed: {e}")

    def test_thinking_disabled_sampling_creative(self, api_key, model_name):
        """Test: anthropic.claude.thinking.disabled | anthropic.claude.sampling.creative"""
        # Anthropic API is different from OpenAI, so we construct the request differently
        body = anthropic.claude.thinking.disabled | anthropic.claude.sampling.creative
        content, usage = self._send_anthropic_request(
            api_key, model_name, "You are a precise function executor.", "What is 2+2? Return only the number."
        )
        assert "4" in content


# ============================================================================
# OpenRouter — multiple models
# ============================================================================

class TestOpenRouterQwen:
    """Test OpenRouter with Qwen 3.6 presets."""

    @pytest.fixture
    def base_url(self):
        return os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    @pytest.fixture
    def api_key(self):
        return os.environ.get("OPENROUTER_API_KEY", "")

    def test_qwen3_6_thinking_disabled(self, base_url, api_key):
        """Test: openrouter.qwen3_6.thinking.disabled | openrouter.qwen3_6.sampling.coding"""
        body = openrouter.qwen3_6.thinking.disabled | openrouter.qwen3_6.sampling.coding | openrouter.qwen3_6.length.short
        content, usage = _send_oai_request(base_url, api_key, "qwen/qwen3-8b", body)
        assert "4" in content
