"""Tests for the Inference Engine (Phase 1).

Validates:
1. Prompt building from function signatures
2. Stub detection
3. Guarded parsing
4. Inference pipeline (with mocked backend)
"""

from __future__ import annotations

import inspect
import pytest

from openhosta.agent.inference import (
    build_infer_prompt,
    is_stub,
    parse_guarded,
    execute_inference,
    InferenceResult,
)
from openhosta.agent.capability import CapabilityMetadata, CapabilityType
from openhosta.guarded.wrapper import Guarded


# --------------------------------------------------------------------------- #
# Helper functions for testing
# --------------------------------------------------------------------------- #


def _infer_func_stub(question: str, context: str | None = None) -> str:
    """Stub inference function for testing prompt building."""
    ...


def _infer_func_with_body(x: int, y: int) -> int:
    """Non-stub function that should not be delegated."""
    return x + y


def _infer_func_typed(data: dict, count: int) -> list[str]:
    """Typed inference with structured return."""
    ...


def _infer_func_complex(items: list[int]) -> dict[str, int]:
    """Complex types inference."""
    ...


# --------------------------------------------------------------------------- #
# Test prompt building
# --------------------------------------------------------------------------- #


class TestBuildInferPrompt:
    def test_basic_prompt_structure(self) -> None:
        meta = CapabilityMetadata(
            name="test.analyze",
            capacity_type=CapabilityType.INFERENCE,
            description="Analyze text",
            tags=["test"],
        )
        prompt = build_infer_prompt(_infer_func_stub, meta, "test question")
        assert "test.analyze" in prompt
        assert "Analyze text" in prompt
        assert "test question" in prompt

    def test_prompt_with_kwargs(self) -> None:
        meta = CapabilityMetadata(
            name="test.kw",
            capacity_type=CapabilityType.INFERENCE,
            tags=[],
        )
        prompt = build_infer_prompt(
            _infer_func_stub,
            meta,
            question="hello",
            context="world"
        )
        assert "question" in prompt
        assert "hello" in prompt
        assert "context" in prompt
        assert "world" in prompt

    def test_prompt_with_typed_function(self) -> None:
        meta = CapabilityMetadata(
            name="test.typed",
            capacity_type=CapabilityType.INFERENCE,
            tags=[],
        )
        prompt = build_infer_prompt(
            _infer_func_typed,
            meta,
            data={"key": "value"},
            count=42
        )
        assert "data" in prompt
        assert "count" in prompt
        assert "list" in prompt.lower()  # return type hint

    def test_prompt_includes_system_instruction(self) -> None:
        meta = CapabilityMetadata(
            name="test.sys",
            capacity_type=CapabilityType.INFERENCE,
            tags=[],
        )
        prompt = build_infer_prompt(_infer_func_stub, meta, "q")
        assert "ONLY the result" in prompt
        assert "no explanations" in prompt.lower()


# --------------------------------------------------------------------------- #
# Test stub detection
# --------------------------------------------------------------------------- #


class TestIsStub:
    def test_stub_with_ellipsis(self) -> None:
        assert is_stub(_infer_func_stub) is True

    def test_stub_with_complex_return(self) -> None:
        assert is_stub(_infer_func_typed) is True
        assert is_stub(_infer_func_complex) is True

    def test_non_stub_with_body(self) -> None:
        assert is_stub(_infer_func_with_body) is False

    def test_builtin_not_stub(self) -> None:
        assert is_stub(len) is False


# --------------------------------------------------------------------------- #
# Test guarded parsing
# --------------------------------------------------------------------------- #


class TestParseGuarded:
    def test_parse_simple_string(self) -> None:
        value, meta = parse_guarded("hello world", str)
        assert "hello" in str(value).lower() or "hello" in str(value)
        assert meta.sources

    def test_parse_integer(self) -> None:
        value, meta = parse_guarded("42", int)
        # Value should be guarded
        assert meta.sources

    def test_parse_none_annotation(self) -> None:
        value, meta = parse_guarded("anything", inspect.Signature.empty)
        assert value is not None

    def test_parse_json_dict(self) -> None:
        value, meta = parse_guarded('{"key": 42}', dict)
        assert meta.sources


# --------------------------------------------------------------------------- #
# Test inference result
# --------------------------------------------------------------------------- #


class TestInferenceResult:
    def test_successful_result(self) -> None:
        result = InferenceResult(success=True, value="test", raw_response="test")
        assert result.success
        assert result.value == "test"
        assert result.error is None

    def test_failed_result(self) -> None:
        result = InferenceResult(
            success=False,
            error=ValueError("bad"),
        )
        assert not result.success
        assert isinstance(result.error, ValueError)


# --------------------------------------------------------------------------- #
# Test full pipeline (mocked)
# --------------------------------------------------------------------------- #


class TestExecuteInference:
    def test_inference_raises_without_backend(self) -> None:
        """When backend URL is invalid, pipeline should fail gracefully."""
        from openhosta.backend import BackendModel

        backend = BackendModel(
            provider="test",
            model_name="test-model",
            base_url="http://invalid-host:9999/v1",
            api_key="",
        )
        meta = CapabilityMetadata(
            name="test.fail",
            capacity_type=CapabilityType.INFERENCE,
            tags=[],
        )

        result = execute_inference(_infer_func_stub, meta, backend, "question")
        assert not result.success
        assert result.error is not None
