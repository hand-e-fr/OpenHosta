"""Tests for CapabilityDispatcher — Phase 2 dispatch and routing."""

import pytest

from next_v5.agent import (
    CapabilityDispatcher,
    CapabilityMetadata,
    CapabilityRegistration,
    CapabilityType,
    tool,
)


@pytest.fixture(autouse=True)
def _clean_registry() -> None:
    """Ensure a clean global registry before and after every test."""
    reg = CapabilityRegistration()
    reg.clear()
    yield
    reg.clear()


# --------------------------------------------------------------------------- #
# Helpers — manual registration without using auto-decorators
# --------------------------------------------------------------------------- #


def _register_capability(
    registry: CapabilityRegistration,
    name: str,
    capacity_type: CapabilityType,
    func: object,
    tags: list[str] | None = None,
    priority: int = 0,
) -> None:
    """Register *func* on *registry* with given metadata (bypass auto-register)."""
    meta = CapabilityMetadata(
        name=name,
        capacity_type=capacity_type,
        tags=tuple(tags) if tags is not None else (),
        priority=priority,
    )
    registry.register(func, meta)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# TestDispatcherInit
# --------------------------------------------------------------------------- #


class TestDispatcherInit:
    def test_default_uses_singleton(self) -> None:
        d = CapabilityDispatcher()
        assert d.registry is CapabilityRegistration()

    def test_custom_registry(self) -> None:
        reg = CapabilityRegistration()
        d = CapabilityDispatcher(registry=reg)
        assert d.registry is reg


# --------------------------------------------------------------------------- #
# TestDispatch
# --------------------------------------------------------------------------- #


class TestDispatch:
    def test_dispatch_existing(self) -> None:
        def multiply(v: int) -> int:
            return v * 2

        reg = CapabilityRegistration()
        _register_capability(reg, "disp.mul", CapabilityType.TOOL, multiply)
        d = CapabilityDispatcher(registry=reg)
        result = d.dispatch("disp.mul", v=5)
        assert result.success is True
        assert result.result == 10
        assert result.error is None
        assert result.metadata is not None
        assert result.metadata.name == "disp.mul"

    def test_dispatch_nonexistent(self) -> None:
        reg = CapabilityRegistration()
        d = CapabilityDispatcher(registry=reg)
        result = d.dispatch("nonexistent")
        assert result.success is False
        assert isinstance(result.error, KeyError)
        assert result.metadata is None

    def test_dispatch_with_kwargs(self) -> None:
        def add(a: int, b: int = 0) -> int:
            return a + b

        reg = CapabilityRegistration()
        _register_capability(reg, "disp.add", CapabilityType.TOOL, add)
        d = CapabilityDispatcher(registry=reg)
        result = d.dispatch("disp.add", a=3, b=7)
        assert result.success is True
        assert result.result == 10

    def test_dispatch_catches_exception(self) -> None:
        def boom() -> int:
            raise ValueError("boom")

        reg = CapabilityRegistration()
        _register_capability(reg, "disp.error", CapabilityType.TOOL, boom)
        d = CapabilityDispatcher(registry=reg)
        result = d.dispatch("disp.error")
        assert result.success is False
        assert isinstance(result.error, ValueError)
        assert result.metadata is not None


# --------------------------------------------------------------------------- #
# TestRouteByType
# --------------------------------------------------------------------------- #


class TestRouteByType:
    def test_route_tools(self) -> None:
        def tool_a(v: int) -> int:
            return v * 2

        def tool_b(v: int) -> int:
            return v * 3

        reg = CapabilityRegistration()
        _register_capability(reg, "disp.ta", CapabilityType.TOOL, tool_a, priority=1)
        _register_capability(reg, "disp.tb", CapabilityType.TOOL, tool_b, priority=2)
        d = CapabilityDispatcher(registry=reg)
        results = d.route_by_type(CapabilityType.TOOL, v=4)
        assert len(results) == 2
        assert results[0].result == 8  # 4*2
        assert results[1].result == 12  # 4*3

    def test_route_inference(self) -> None:
        def inference(v: int) -> int:
            return v + 100

        reg = CapabilityRegistration()
        _register_capability(reg, "disp.inf", CapabilityType.INFERENCE, inference)
        d = CapabilityDispatcher(registry=reg)
        results = d.route_by_type(CapabilityType.INFERENCE, v=1)
        assert len(results) == 1
        assert results[0].result == 101

    def test_route_playbook(self) -> None:
        def pb() -> str:
            return "pb"

        reg = CapabilityRegistration()
        _register_capability(reg, "disp.pb", CapabilityType.PLAYBOOK, pb)
        d = CapabilityDispatcher(registry=reg)
        results = d.route_by_type(CapabilityType.PLAYBOOK)
        assert len(results) == 1
        assert results[0].result == "pb"

    def test_route_empty_type(self) -> None:
        reg = CapabilityRegistration()
        d = CapabilityDispatcher(registry=reg)
        results = d.route_by_type(CapabilityType.ROUTER)
        assert results == []

    def test_route_priority_order(self) -> None:
        def high() -> int:
            return 0

        def low() -> int:
            return 1

        reg = CapabilityRegistration()
        _register_capability(reg, "disp.high", CapabilityType.TOOL, high, priority=1)
        _register_capability(reg, "disp.low", CapabilityType.TOOL, low, priority=0)
        d = CapabilityDispatcher(registry=reg)
        results = d.route_by_type(CapabilityType.TOOL)
        # Priority 0 first
        assert results[0].result == 1
        assert results[1].result == 0
        assert results[0].metadata is not None
        assert results[0].metadata.priority < results[1].metadata.priority


# --------------------------------------------------------------------------- #
# TestRouteByTag
# --------------------------------------------------------------------------- #


class TestRouteByTag:
    def test_route_tag_x(self) -> None:
        def ta(v: int) -> int:
            return v * 2

        def inf(v: int) -> int:
            return v + 100

        reg = CapabilityRegistration()
        _register_capability(reg, "disp.ta", CapabilityType.TOOL, ta, tags=["x", "t"])
        _register_capability(reg, "disp.inf", CapabilityType.INFERENCE, inf, tags=["x"])
        d = CapabilityDispatcher(registry=reg)
        results = d.route_by_tag("x", v=2)
        assert len(results) == 2

    def test_route_tag_y(self) -> None:
        def tb(v: int) -> int:
            return v * 3

        def ta(v: int) -> int:
            return v * 2

        reg = CapabilityRegistration()
        _register_capability(reg, "disp.tb", CapabilityType.TOOL, tb, tags=["y", "t"])
        _register_capability(reg, "disp.ta", CapabilityType.TOOL, ta, tags=["x", "t"])
        d = CapabilityDispatcher(registry=reg)
        results = d.route_by_tag("y", v=3)
        assert len(results) == 1
        assert results[0].result == 9

    def test_route_tag_none(self) -> None:
        reg = CapabilityRegistration()
        d = CapabilityDispatcher(registry=reg)
        results = d.route_by_tag("nonexistent")
        assert results == []

    def test_route_tag_catches_error(self) -> None:
        def bad() -> int:
            raise RuntimeError("fail")

        reg = CapabilityRegistration()
        _register_capability(reg, "disp.bad", CapabilityType.TOOL, bad, tags=["err_tag"])
        d = CapabilityDispatcher(registry=reg)
        results = d.route_by_tag("err_tag")
        assert len(results) == 1
        assert results[0].success is False
        assert isinstance(results[0].error, RuntimeError)


# --------------------------------------------------------------------------- #
# TestDispatcherProperties
# --------------------------------------------------------------------------- #


class TestDispatcherProperties:
    def test_capability_count(self) -> None:
        def f() -> int:
            return 1

        reg = CapabilityRegistration()
        _register_capability(reg, "disp.c1", CapabilityType.TOOL, f)
        d = CapabilityDispatcher(registry=reg)
        assert d.capability_count() == 1

    def test_list_capabilities(self) -> None:
        def f() -> int:
            return 1

        def g() -> str:
            return "hello"

        reg = CapabilityRegistration()
        _register_capability(reg, "disp.c1", CapabilityType.TOOL, f)
        _register_capability(reg, "disp.c2", CapabilityType.TOOL, g)
        d = CapabilityDispatcher(registry=reg)
        metas = d.list_capabilities()
        assert len(metas) == 2
        names = {m.name for m in metas}
        assert names == {"disp.c1", "disp.c2"}


# --------------------------------------------------------------------------- #
# TestDecoratorAutoRegistration
# --------------------------------------------------------------------------- #


class TestDecoratorAutoRegistration:
    """Verify that decorators auto-register in the global registry."""

    def test_tool_auto_registers(self) -> None:
        @tool(name="auto.tool", description="auto-registered tool")
        def auto_tool(x: int) -> int:
            return x + 1

        reg = CapabilityRegistration()
        assert reg.count == 1
        func, meta = reg.get("auto.tool")
        assert meta.capacity_type == CapabilityType.TOOL
        assert func(4) == 5  # noqa: PLR2004
