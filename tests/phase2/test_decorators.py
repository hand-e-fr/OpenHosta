"""Tests for capability decorators and registry — Phase 2 capabilities."""

from dataclasses import FrozenInstanceError

import pytest

from next_v5.agent import (
    CapabilityMetadata,
    CapabilityRegistration,
    CapabilityType,
    infer,
    planner,
    playbook,
    router,
    tool,
)


@pytest.fixture(autouse=True)
def _clean_registry() -> None:
    """Ensure a clean registry before and after every test."""
    reg = CapabilityRegistration()
    reg.clear()
    yield
    reg.clear()


# --------------------------------------------------------------------------- #
# Helpers — decorated functions used by the tests below
# --------------------------------------------------------------------------- #


def _make_tool(name: str) -> None:
    tool(name=name, description="test tool")(_noop)  # noqa: ARG005


def _make_infer(name: str) -> None:
    infer(name=name, description="test infer")(_noop)  # noqa: ARG005


def _make_playbook(name: str) -> None:
    playbook(name=name, description="test playbook")(_noop)  # noqa: ARG005


def _make_planner(name: str) -> None:
    planner(name=name, description="test planner")(_noop)  # noqa: ARG005


def _make_router(name: str) -> None:
    router(name=name, description="test router")(_noop)  # noqa: ARG005


def _noop() -> str:
    return "noop"


# --------------------------------------------------------------------------- #
# TestCapabilityType
# --------------------------------------------------------------------------- #


class TestCapabilityType:
    def test_tool_exists(self) -> None:
        assert CapabilityType.TOOL is not None

    def test_inference_exists(self) -> None:
        assert CapabilityType.INFERENCE is not None

    def test_playbook_exists(self) -> None:
        assert CapabilityType.PLAYBOOK is not None

    def test_planner_exists(self) -> None:
        assert CapabilityType.PLANNER is not None

    def test_router_exists(self) -> None:
        assert CapabilityType.ROUTER is not None

    def test_all_distinct(self) -> None:
        members = list(CapabilityType)
        assert len(members) == 5
        assert len(set(members)) == 5


# --------------------------------------------------------------------------- #
# TestCapabilityMetadata
# --------------------------------------------------------------------------- #


class TestCapabilityMetadata:
    def test_defaults(self) -> None:
        meta = CapabilityMetadata(name="x", capacity_type=CapabilityType.TOOL)
        assert meta.description == ""
        assert meta.tags == ()
        assert meta.priority == 0
        assert meta.requires_async is False

    def test_custom(self) -> None:
        meta = CapabilityMetadata(
            name="y",
            capacity_type=CapabilityType.INFERENCE,
            description="cool",
            tags=("a", "b"),
            priority=5,
            requires_async=True,
        )
        assert meta.tag_set == {"a", "b"}
        assert meta.priority == 5

    def test_frozen(self) -> None:
        meta = CapabilityMetadata(name="z", capacity_type=CapabilityType.TOOL)
        with pytest.raises(FrozenInstanceError):
            meta.name = "changed"  # type: ignore[misc]


# --------------------------------------------------------------------------- #
# TestDecoratorTool
# --------------------------------------------------------------------------- #


class TestDecoratorTool:
    def test_decorator_registers(self) -> None:
        _make_tool("test.decorators.tool")
        reg = CapabilityRegistration()
        assert reg.count == 1
        func, meta = reg.get("test.decorators.tool")
        assert func is not None
        assert meta.capacity_type == CapabilityType.TOOL

    def test_decorator_preserves_function(self) -> None:
        _make_tool("test.decorators.tool2")
        reg = CapabilityRegistration()
        func, _ = reg.get("test.decorators.tool2")
        assert func() == "noop"

    def test_decorator_attach_metadata(self) -> None:
        _make_tool("test.decorators.tool3")
        reg = CapabilityRegistration()
        func, _ = reg.get("test.decorators.tool3")
        assert hasattr(func, "_capability")
        assert func._capability.name == "test.decorators.tool3"


# --------------------------------------------------------------------------- #
# TestDecoratorInfer
# --------------------------------------------------------------------------- #


class TestDecoratorInfer:
    def test_decorator_registers(self) -> None:
        _make_infer("test.decorators.infer")
        reg = CapabilityRegistration()
        _, meta = reg.get("test.decorators.infer")
        assert meta.capacity_type == CapabilityType.INFERENCE


# --------------------------------------------------------------------------- #
# TestDecoratorPlaybook
# --------------------------------------------------------------------------- #


class TestDecoratorPlaybook:
    def test_decorator_registers(self) -> None:
        _make_playbook("test.decorators.playbook")
        reg = CapabilityRegistration()
        _, meta = reg.get("test.decorators.playbook")
        assert meta.capacity_type == CapabilityType.PLAYBOOK


# --------------------------------------------------------------------------- #
# TestDecoratorPlanner
# --------------------------------------------------------------------------- #


class TestDecoratorPlanner:
    def test_decorator_registers(self) -> None:
        _make_planner("test.decorators.planner")
        reg = CapabilityRegistration()
        _, meta = reg.get("test.decorators.planner")
        assert meta.capacity_type == CapabilityType.PLANNER


# --------------------------------------------------------------------------- #
# TestDecoratorRouter
# --------------------------------------------------------------------------- #


class TestDecoratorRouter:
    def test_decorator_registers(self) -> None:
        _make_router("test.decorators.router")
        reg = CapabilityRegistration()
        _, meta = reg.get("test.decorators.router")
        assert meta.capacity_type == CapabilityType.ROUTER


# --------------------------------------------------------------------------- #
# TestCapabilityRegistration
# --------------------------------------------------------------------------- #


class TestCapabilityRegistration:
    def test_singleton(self) -> None:
        a = CapabilityRegistration()
        b = CapabilityRegistration()
        assert a is b

    def test_duplicate_registration_raises(self) -> None:
        _make_tool("test.dup.tool")
        with pytest.raises(ValueError, match="already registered"):
            _make_tool("test.dup.tool")

    def test_get_unknown_raises(self) -> None:
        reg = CapabilityRegistration()
        with pytest.raises(KeyError, match="not found"):
            reg.get("nonexistent")

    def test_find_by_name_returns_none(self) -> None:
        reg = CapabilityRegistration()
        assert reg.find_by_name("nonexistent") is None

    def test_find_by_type(self) -> None:
        _make_tool("test.type.a")
        _make_tool("test.type.b")
        _make_infer("test.type.c")
        reg = CapabilityRegistration()
        tools = reg.find_by_type(CapabilityType.TOOL)
        inferences = reg.find_by_type(CapabilityType.INFERENCE)
        assert len(tools) == 2
        assert len(inferences) == 1

    def test_find_by_tag(self) -> None:
        reg = CapabilityRegistration()
        tool(name="test.tag.a", description="", tags=["x", "y"])(_noop)  # noqa: ARG005
        tool(name="test.tag.b", description="", tags=["x"])(_noop)  # noqa: ARG005
        tool(name="test.tag.c", description="", tags=["y"])(_noop)  # noqa: ARG005
        by_x = reg.find_by_tag("x")
        by_y = reg.find_by_tag("y")
        by_z = reg.find_by_tag("z")
        assert len(by_x) == 2
        assert len(by_y) == 2
        assert len(by_z) == 0

    def test_list_all(self) -> None:
        _make_tool("test.list.a")
        _make_infer("test.list.b")
        reg = CapabilityRegistration()
        assert len(reg.list_all()) == 2

    def test_count(self) -> None:
        _make_tool("test.count.a")
        reg = CapabilityRegistration()
        assert reg.count == 1

    def test_clear(self) -> None:
        _make_tool("test.clear.a")
        reg = CapabilityRegistration()
        assert reg.count == 1
        reg.clear()
        assert reg.count == 0


# --------------------------------------------------------------------------- #
# TestDecoratorArguments
# --------------------------------------------------------------------------- #


class TestDecoratorArguments:
    def test_description_stored(self) -> None:
        tool(name="test.args.desc", description="a description")(_noop)  # noqa: ARG005
        reg = CapabilityRegistration()
        _, meta = reg.get("test.args.desc")
        assert meta.description == "a description"

    def test_priority_stored(self) -> None:
        tool(name="test.args.prio", priority=42)(_noop)  # noqa: ARG005
        reg = CapabilityRegistration()
        _, meta = reg.get("test.args.prio")
        assert meta.priority == 42

    def test_requires_async_stored(self) -> None:
        infer(name="test.args.async", requires_async=True)(_noop)  # noqa: ARG005
        reg = CapabilityRegistration()
        _, meta = reg.get("test.args.async")
        assert meta.requires_async is True

    def test_tags_tuple(self) -> None:
        tool(name="test.args.tags", tags=["a", "b", "c"])(_noop)  # noqa: ARG005
        reg = CapabilityRegistration()
        _, meta = reg.get("test.args.tags")
        assert meta.tags == ("a", "b", "c")
