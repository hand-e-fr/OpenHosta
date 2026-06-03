"""Tests for BackendModel, BackendSelector, and BackendModel.compile()."""

import pytest

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
