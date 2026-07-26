"""Tests for BackendModel, BackendSelector, and BackendModel.compile()."""

import json
import pytest

from openhosta.agent.capability import CapabilityType
from openhosta.backend import BackendModel, BackendSelector


class TestBackendModel:
    def test_stores_attributes(self) -> None:
        bm = BackendModel(
            provider="openai",
            model_name="gpt-4",
            base_url="https://api.openai.com/v1",
            api_key="sk-test",
            tags=("fast", "expensive"),
            priority=10,
        )
        assert bm.provider == "openai"
        assert bm.model_name == "gpt-4"
        assert bm.base_url == "https://api.openai.com/v1"
        assert bm.api_key == "sk-test"
        assert bm.tags == ("fast", "expensive")
        assert bm.priority == 10

    def test_default_api_key_and_tags(self) -> None:
        bm = BackendModel(
            provider="local",
            model_name="llama",
            base_url="http://127.0.0.1:8000/v1",
        )
        assert bm.api_key == ""
        assert bm.tags == ()
        assert bm.priority == 0

    def test_tag_set(self) -> None:
        bm = BackendModel(
            provider="x",
            model_name="m",
            base_url="http://example.com",
            tags=("a", "b", "a"),
        )
        assert bm.tag_set == {"a", "b"}

    def test_compile_returns_decorator(self) -> None:
        bm = BackendModel(
            provider="x",
            model_name="m",
            base_url="http://example.com",
        )
        decorator = bm.compile()
        assert callable(decorator)

    def test_compile_marks_class(self) -> None:
        bm = BackendModel(
            provider="x",
            model_name="m",
            base_url="http://example.com",
        )

        @bm.compile()
        class MyAgent:
            pass

        assert hasattr(MyAgent, "_backend")
        assert MyAgent._backend is bm

    def test_compile_preserves_class_identity(self) -> None:
        bm = BackendModel(
            provider="x",
            model_name="m",
            base_url="http://example.com",
        )

        class OriginalAgent:
            pass

        WrappedAgent = bm.compile()(OriginalAgent)
        assert WrappedAgent.__name__ == "OriginalAgent"


# -- Introspection tests --


class TestCapabilityRegistration:
    def test_empty_by_default(self) -> None:
        bm = BackendModel("x", "m", "http://example.com")
        assert bm.cap_count == 0
        assert bm.capabilities == []

    def test_infer_registers_capability(self) -> None:
        bm = BackendModel("x", "m", "http://example.com")

        @bm.infer()
        def summarize(text: str) -> str:
            """Summarize text."""
            return text[:10]

        assert bm.cap_count == 1
        meta = bm.get_capability("summarize")
        assert meta.name == "summarize"
        assert meta.capacity_type == CapabilityType.INFERENCE
        assert meta.description == "Summarize text."

    def test_infer_registers_stub(self) -> None:
        bm = BackendModel("x", "m", "http://example.com")

        @bm.infer()
        def classify(text: str) -> str:
            """Classify text by topic."""
            ...

        assert bm.cap_count == 1
        meta = bm.get_capability("classify")
        assert meta.capacity_type == CapabilityType.INFERENCE
        assert meta.name == "classify"

    def test_infer_custom_name_and_description(self) -> None:
        bm = BackendModel("x", "m", "http://example.com")

        @bm.infer(name="my_summarize", description="Custom summary")
        def summarize(text: str) -> str:
            """Docstring."""
            return text[:10]

        meta = bm.get_capability("my_summarize")
        assert meta.name == "my_summarize"
        assert meta.description == "Custom summary"

    def test_infer_with_tags(self) -> None:
        bm = BackendModel("x", "m", "http://example.com")

        @bm.infer(tags=["lang", "fr"])
        def translate(text: str) -> str:
            """Translate text."""
            return text

        @bm.infer(tags=["summary"])
        def summarize(text: str) -> str:
            """Summarize text."""
            return text[:10]

        lang_caps = bm.find_by_tag("lang")
        assert len(lang_caps) == 1
        assert lang_caps[0].name == "translate"

        summary_caps = bm.find_by_tag("summary")
        assert len(summary_caps) == 1
        assert summary_caps[0].name == "summarize"

    def test_tool_registers(self) -> None:
        bm = BackendModel("x", "m", "http://example.com")

        @bm.tool(tags=["files"])
        def read_file(path: str) -> str:
            """Read a file."""
            return ""

        assert bm.cap_count == 1
        meta = bm.get_capability("read_file")
        assert meta.capacity_type == CapabilityType.TOOL
        assert meta.tags == ("files",)

    def test_planner_registers(self) -> None:
        bm = BackendModel("x", "m", "http://example.com")

        @bm.planner()
        def plan(goal: str) -> list[str]:
            """Plan steps to achieve goal."""
            ...

        assert bm.cap_count == 1
        meta = bm.get_capability("plan")
        assert meta.capacity_type == CapabilityType.PLANNER

    def test_router_registers(self) -> None:
        bm = BackendModel("x", "m", "http://example.com")

        @bm.router()
        def route(msg: str) -> str:
            """Route message to correct handler."""
            ...

        assert bm.cap_count == 1
        meta = bm.get_capability("route")
        assert meta.capacity_type == CapabilityType.ROUTER

    def test_playbook_registers(self) -> None:
        bm = BackendModel("x", "m", "http://example.com")

        @bm.playbook()
        def pipeline(text: str) -> str:
            """Multi-step pipeline."""
            return text

        assert bm.cap_count == 1
        meta = bm.get_capability("pipeline")
        assert meta.capacity_type == CapabilityType.PLAYBOOK

    def test_find_by_type(self) -> None:
        bm = BackendModel("x", "m", "http://example.com")

        @bm.infer()
        def summarize(text: str) -> str:
            """Summarize text."""
            return text[:10]

        @bm.tool()
        def read_file(path: str) -> str:
            """Read a file."""
            return ""

        @bm.infer()
        def translate(text: str) -> str:
            """Translate text."""
            return text

        infer_caps = bm.find_by_type(CapabilityType.INFERENCE)
        assert len(infer_caps) == 2
        assert {m.name for m in infer_caps} == {"summarize", "translate"}

        tool_caps = bm.find_by_type(CapabilityType.TOOL)
        assert len(tool_caps) == 1
        assert tool_caps[0].name == "read_file"

    def test_find_capability_returns_none_for_missing(self) -> None:
        bm = BackendModel("x", "m", "http://example.com")
        assert bm.find_capability("nonexistent") is None

    def test_get_capability_raises_for_missing(self) -> None:
        bm = BackendModel("x", "m", "http://example.com")
        with pytest.raises(KeyError, match="not found in registry"):
            bm.get_capability("nonexistent")

    def test_multiple_decorators_same_model(self) -> None:
        bm = BackendModel("x", "m", "http://example.com")

        @bm.infer(tags=["lang"])
        def translate(text: str) -> str:
            """Translate text."""
            return text

        @bm.tool(tags=["files"])
        def read_file(path: str) -> str:
            """Read a file."""
            return ""

        @bm.planner(tags=["plan"])
        def plan(goal: str) -> list[str]:
            """Plan steps."""
            ...

        assert bm.cap_count == 3

    def test_long_description_contains_docstring_and_signature(self) -> None:
        bm = BackendModel("x", "m", "http://example.com")

        @bm.infer()
        def translate(text: str, target_lang: str) -> str:
            """Translate text into target_lang.

            Returns the translated text.
            """
            return text

        meta = bm.get_capability("translate")
        assert "translate" in meta.long_description
        assert "text: str" in meta.long_description
        assert "target_lang: str" in meta.long_description
        assert "Translate text into target_lang" in meta.long_description


# -- to_dict / serialization tests --


class TestSerialization:
    def test_to_dict(self) -> None:
        bm = BackendModel("openai", "gpt-4", "https://api.openai.com/v1")

        @bm.infer(tags=["lang"])
        def translate(text: str) -> str:
            """Translate text."""
            return text

        @bm.tool(tags=["files"])
        def read_file(path: str) -> str:
            """Read a file."""
            return ""

        d = bm.to_dict()
        assert d["provider"] == "openai"
        assert d["model_name"] == "gpt-4"
        assert d["base_url"] == "https://api.openai.com/v1"
        assert len(d["capabilities"]) == 2

        cap0 = d["capabilities"][0]
        assert cap0["type"] == "INFERENCE"
        assert cap0["tags"] == ["lang"]

        cap1 = d["capabilities"][1]
        assert cap1["type"] == "TOOL"
        assert cap1["tags"] == ["files"]

    def test_to_dict_is_json_serializable(self) -> None:
        bm = BackendModel("openai", "gpt-4", "https://api.openai.com/v1")

        @bm.infer(tags=["lang"])
        def translate(text: str) -> str:
            """Translate text."""
            return text

        d = bm.to_dict()
        json_str = json.dumps(d)
        assert "translate" in json_str
        assert "INFERENCE" in json_str


# -- Misuse detection tests --


class TestMisuseDetection:
    def test_infer_missing_parens(self) -> None:
        bm = BackendModel("x", "m", "http://example.com")
        with pytest.raises(TypeError, match="Missing parentheses"):
            bm.infer(lambda x: x)

    def test_tool_missing_parens(self) -> None:
        bm = BackendModel("x", "m", "http://example.com")
        with pytest.raises(TypeError, match="Missing parentheses"):
            bm.tool(lambda x: x)

    def test_planner_missing_parens(self) -> None:
        bm = BackendModel("x", "m", "http://example.com")
        with pytest.raises(TypeError, match="Missing parentheses"):
            bm.planner(lambda x: x)

    def test_router_missing_parens(self) -> None:
        bm = BackendModel("x", "m", "http://example.com")
        with pytest.raises(TypeError, match="Missing parentheses"):
            bm.router(lambda x: x)

    def test_playbook_missing_parens(self) -> None:
        bm = BackendModel("x", "m", "http://example.com")
        with pytest.raises(TypeError, match="Missing parentheses"):
            bm.playbook(lambda x: x)


class TestBackendSelector:
    def test_rejects_empty_candidates(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            BackendSelector([])

    def test_resolve_no_constraints_returns_first(self) -> None:
        bm1 = BackendModel("p1", "m1", "u1")
        bm2 = BackendModel("p2", "m2", "u2")
        sel = BackendSelector([bm1, bm2])
        assert sel.resolve() is bm1

    def test_resolve_no_constraints_none(self) -> None:
        bm = BackendModel("p1", "m1", "u1")
        sel = BackendSelector([bm])
        assert sel.resolve(None) is bm

    def test_resolve_by_tag(self) -> None:
        bm1 = BackendModel("p1", "m1", "u1", tags=("fast",))
        bm2 = BackendModel("p2", "m2", "u2", tags=("cheap",))
        sel = BackendSelector([bm1, bm2])
        result = sel.resolve(constraints={"tags": ["cheap"]})
        assert result is bm2

    def test_resolve_tag_no_match_fallback(self) -> None:
        bm = BackendModel("p1", "m1", "u1", tags=("fast",))
        sel = BackendSelector([bm])
        result = sel.resolve(constraints={"tags": ["unknown"]})
        assert result is bm

    def test_resolve_empty_constraints_dict(self) -> None:
        bm = BackendModel("p1", "m1", "u1")
        sel = BackendSelector([bm])
        assert sel.resolve(constraints={}) is bm
