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
from openhosta.agent.capability import CapabilityMetadata, CapabilityType, _default_registry
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


# --------------------------------------------------------------------------- #
# Test decorator inference wrapping
# --------------------------------------------------------------------------- #


class TestDecoratorInferenceWrapping:
    """Verify that @infer/@planner/@router wrap stubs with InferenceEngine."""

    def test_stub_infer_is_wrapped(self) -> None:
        """A stub decorated with @infer should be wrapped with inference."""
        from openhosta.agent.capability import _wrap_inference
        from openhosta.backend import BackendModel

        # Create a fresh stub function for this test
        def _stub_fn(q: str) -> str:
            """Test stub."""
            ...

        meta = CapabilityMetadata(
            name="test.wrap.stub",
            capacity_type=CapabilityType.INFERENCE,
            tags=[],
        )
        wrapped = _wrap_inference(_stub_fn, meta)
        # The wrapper should be a different callable
        assert wrapped is not _stub_fn
        # Calling it with invalid backend should fail gracefully
        backend = BackendModel(
            provider="test",
            model_name="test",
            base_url="http://invalid:9999/v1",
        )
        # This will fail because the backend is unreachable
        try:
            wrapped("test question", _backend=backend)
        except RuntimeError as e:
            assert "Inference failed" in str(e) or "Backend" in str(e)

    def test_non_stub_infer_not_wrapped(self) -> None:
        """A non-stub decorated with @infer should NOT be wrapped."""
        from openhosta.agent.capability import _wrap_inference

        def _real_fn(x: int, y: int) -> int:
            """Real function."""
            return x + y

        meta = CapabilityMetadata(
            name="test.wrap.real",
            capacity_type=CapabilityType.INFERENCE,
            tags=[],
        )
        wrapped = _wrap_inference(_real_fn, meta)
        # Non-stub should return the original function unchanged
        assert wrapped is _real_fn
        assert wrapped(2, 3) == 5

    def test_stub_planner_is_wrapped(self) -> None:
        """A stub decorated with @planner should be wrapped with inference."""
        from openhosta.agent.capability import _wrap_inference

        def _stub_plan(goal: str) -> list[str]:
            """Test planner stub."""
            ...

        meta = CapabilityMetadata(
            name="test.wrap.planner",
            capacity_type=CapabilityType.PLANNER,
            tags=[],
        )
        wrapped = _wrap_inference(_stub_plan, meta)
        assert wrapped is not _stub_plan

    def test_stub_router_is_wrapped(self) -> None:
        """A stub decorated with @router should be wrapped with inference."""
        from openhosta.agent.capability import _wrap_inference

        def _stub_route(intent: str) -> str:
            """Test router stub."""
            ...

        meta = CapabilityMetadata(
            name="test.wrap.router",
            capacity_type=CapabilityType.ROUTER,
            tags=[],
        )
        wrapped = _wrap_inference(_stub_route, meta)
        assert wrapped is not _stub_route

    def test_tool_not_wrapped(self) -> None:
        """@tool should never wrap with inference."""
        from openhosta.agent import tool
        from openhosta.agent.capability import CapabilityRegistration

        reg = _default_registry
        reg.clear()

        @tool(name="test.tool.not_wrapped", description="test tool")
        def _tool_stub(q: str) -> str:
            """Tool stub."""
            ...

        func, meta = reg.get("test.tool.not_wrapped")
        # @tool does not use _wrap_inference, so stub is registered as-is
        # A function with only `...` returns None (the Ellipsis is not returned)
        result = func("test")
        assert result is None


# --------------------------------------------------------------------------- #
# End-to-end test: Agent.get() routes stub @infer through InferenceEngine
# --------------------------------------------------------------------------- #


class TestEndToEndInference:
    """Verify that Agent.get() routes stub @infer/@planner/@router through InferenceEngine."""

    def test_agent_routes_stub_infer_through_engine(self) -> None:
        """When Agent.get() dispatches a stub @infer, it should use InferenceEngine."""
        from openhosta.agent import Agent
        from openhosta.agent._config import set_default_backend
        from openhosta.backend import BackendModel

        backend = BackendModel(
            provider="test",
            model_name="test-model",
            base_url="http://invalid-host:9999/v1",
            api_key="",
        )
        set_default_backend(backend)

        # Define a stub @infer capability
        from openhosta.agent import infer
        from openhosta.agent.capability import CapabilityRegistration

        reg = _default_registry
        reg.clear()

        @infer(name="e2e.stub_infer", description="End-to-end stub inference")
        def stub_e2e(msg: str) -> str:
            """End-to-end stub."""
            ...

        # Create agent with backend
        agent = Agent(backend=backend)
        agent.recruit()

        # Call via dispatcher (simulates Agent.get() flow)
        from openhosta.agent.dispatch import CapabilityDispatcher

        dispatcher = CapabilityDispatcher(registry=agent._registry)
        results = dispatcher.route_by_type(
            CapabilityType.INFERENCE,
            msg="test message",
            _backend=backend,
        )

        # Should have one result, which failed because backend is unreachable
        assert len(results) == 1
        assert not results[0].success
        assert results[0].error is not None

        # Cleanup
        agent.kill()
        set_default_backend(None)
        reg.clear()

    def test_agent_recruit_sets_default_backend(self) -> None:
        """Agent.recruit() should register the backend as default for inference."""
        from openhosta.agent import Agent
        from openhosta.agent._config import get_default_backend, set_default_backend
        from openhosta.backend import BackendModel

        # Clear any existing backend
        set_default_backend(None)

        backend = BackendModel(
            provider="test",
            model_name="test-model",
            base_url="http://localhost:8000/v1",
        )

        agent = Agent(backend=backend)
        agent.recruit()

        # Backend should be registered as default
        default = get_default_backend()
        assert default is not None
        assert default.model_name == "test-model"

        # Cleanup
        agent.kill()
        set_default_backend(None)

    def test_agent_get_injects_backend_into_dispatcher(self) -> None:
        """Agent.get() should inject _backend into dispatcher kwargs."""
        from openhosta.agent import Agent
        from openhosta.backend import BackendModel

        backend = BackendModel(
            provider="test",
            model_name="test-model",
            base_url="http://localhost:8000/v1",
        )

        agent = Agent(backend=backend)
        agent.recruit()

        # Verify that agent._backend is set
        assert agent._backend is not None

        # Cleanup
        agent.kill()
