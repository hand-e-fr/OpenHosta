"""Tests for downstream module — Dependency, DownstreamContext, AgentGraph.

REQ-DOWNSTREAM-001 — Dependency graph with lazy/eager evaluation and heritage
context inheritance through agent hierarchies
"""

from __future__ import annotations

from typing import Any

import pytest

from openhosta.agent.downstream import (
    AgentGraph,
    DependencyMode,
    DownstreamContext,
    MissingDependencyError,
    ResolutionResult,
    TopologyLog,
    eager,
    lazy,
)

# ============================================================================
# TestDependencyConstructors
# ============================================================================


class TestDependencyConstructors:
    def test_lazy_creates_lazy_mode(self) -> None:
        dep = lazy("a")
        assert dep.mode == DependencyMode.LAZY

    def test_eager_creates_eager_mode(self) -> None:
        dep = eager("b")
        assert dep.mode == DependencyMode.EAGER

    def test_lazy_inherits_tuple_default(self) -> None:
        dep = lazy("a")
        assert dep.inherits == ()

    def test_lazy_inherits_tuple_from_list(self) -> None:
        dep = lazy("a", inherits=["k1", "k2"])
        assert dep.inherits == ("k1", "k2")

    def test_lazy_inherits_tuple_from_tuple(self) -> None:
        dep = lazy("a", inherits=("k1", "k2"))
        assert dep.inherits == ("k1", "k2")

    def test_eager_inherits_tuple_default(self) -> None:
        dep = eager("b")
        assert dep.inherits == ()

    def test_eager_inherits_tuple_from_list(self) -> None:
        dep = eager("b", inherits=["x"])
        assert dep.inherits == ("x",)

    def test_is_lazy_true(self) -> None:
        dep = lazy("a")
        assert dep.is_lazy is True

    def test_is_lazy_false(self) -> None:
        dep = eager("b")
        assert dep.is_lazy is False

    def test_is_eager_true(self) -> None:
        dep = eager("b")
        assert dep.is_eager is True

    def test_is_eager_false(self) -> None:
        dep = lazy("a")
        assert dep.is_eager is False


# ============================================================================
# TestDependencyConstruction
# ============================================================================


class TestDependency:
    def test_tag_and_priority(self) -> None:
        dep = eager("d1", tag="data", priority=5)
        assert dep.tag == "data"
        assert dep.priority == 5


# ============================================================================
# TestDownstreamContextDefaults
# ============================================================================


class TestDownstreamContextDefaults:
    def test_default_values(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        assert ctx.agent_id == "root"
        assert ctx.parent is None
        assert ctx.heritage == {}
        assert ctx.overrides == {}
        assert ctx.dependencies == []


# ============================================================================
# TestDownstreamContextHeritage
# ============================================================================


class TestDownstreamContextHeritage:
    def test_parent_heritage_is_inherited(self) -> None:
        parent = DownstreamContext(agent_id="parent", heritage={"a": 1, "b": 2})
        child = DownstreamContext(agent_id="child", parent=parent)
        assert child.heritage == {"a": 1, "b": 2}

    def test_child_heritage_overrides_parent(self) -> None:
        parent = DownstreamContext(agent_id="parent", heritage={"a": 1, "b": 2})
        child = DownstreamContext(
            agent_id="child",
            parent=parent,
            heritage={"b": 3, "c": 4},
        )
        assert child.heritage == {"a": 1, "b": 3, "c": 4}

    def test_get_heritage_basic(self) -> None:
        ctx = DownstreamContext(agent_id="root", heritage={"k": "v"})
        assert ctx.get_heritage("k") == "v"

    def test_get_heritage_default(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        assert ctx.get_heritage("missing", "default") == "default"

    def test_get_heritage_respects_override(self) -> None:
        ctx = DownstreamContext(agent_id="root", heritage={"k": "original"})
        ctx.set_override("k", "overridden")
        assert ctx.get_heritage("k") == "overridden"

    def test_set_override(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        ctx.set_override("x", 42)
        assert ctx.overrides["x"] == 42

    def test_effective_heritage_merges_heritage_and_overrides(self) -> None:
        ctx = DownstreamContext(agent_id="root", heritage={"a": 1, "b": 2})
        ctx.set_override("b", 3)
        ctx.set_override("c", 4)
        assert ctx.effective_heritage() == {"a": 1, "b": 3, "c": 4}

    def test_child_heritage_respects_dep_inherits(self) -> None:
        ctx = DownstreamContext(agent_id="root", heritage={"a": 1, "b": 2, "c": 3})
        dep = eager("d1", inherits=("a", "b"))
        child = ctx.child_heritage(dep)
        assert child == {"a": 1, "b": 2}

    def test_child_heritage_empty_inherits_returns_empty(self) -> None:
        ctx = DownstreamContext(agent_id="root", heritage={"a": 1})
        dep = eager("d1")
        child = ctx.child_heritage(dep)
        assert child == {}

    def test_child_heritage_ignores_missing_keys(self) -> None:
        ctx = DownstreamContext(agent_id="root", heritage={"a": 1})
        dep = eager("d1", inherits=("a", "z"))
        child = ctx.child_heritage(dep)
        assert child == {"a": 1}


# ============================================================================
# TestDownstreamContextDependencies
# ============================================================================


class TestDownstreamContextDependencies:
    def test_register_returns_self(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        ret = ctx.register(lazy("a"))
        assert ret is ctx

    def test_register_duplicate_raises_value_error(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        ctx.register(lazy("a"))
        with pytest.raises(ValueError, match="Duplicate dependency 'a'"):
            ctx.register(lazy("a"))

    def test_get_dependency(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        ctx.register(eager("d1"))
        dep = ctx.get_dependency("d1")
        assert dep.name == "d1"

    def test_get_dependency_missing_raises_key_error(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        with pytest.raises(KeyError):
            ctx.get_dependency("missing")

    def test_eager_deps_returns_correct_subset(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        ctx.register(eager("a")).register(lazy("b")).register(eager("c"))
        assert [d.name for d in ctx.eager_deps()] == ["a", "c"]

    def test_lazy_deps_returns_correct_subset(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        ctx.register(eager("a")).register(lazy("b")).register(lazy("c"))
        assert [d.name for d in ctx.lazy_deps()] == ["b", "c"]

    def test_register_callable(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        ctx.register_callable(eager("d1"), lambda context=None: 42)
        dep = ctx.get_dependency("d1")
        assert dep.name == "d1"


# ============================================================================
# TestDownstreamContextResolution
# ============================================================================


class TestDownstreamContextResolution:
    def test_resolve_all_evaluates_eager_deps(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        ctx.register_callable(eager("d1"), lambda context=None: 42)
        ctx.register_callable(eager("d2"), lambda context=None: 99)
        results = ctx.resolve_all()
        assert len(results) == 2
        assert all(r.success for r in results)
        assert {r.result for r in results} == {42, 99}

    def test_resolve_all_sorts_by_priority(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        ctx.register_callable(eager("low", priority=10), lambda context=None: "low")
        ctx.register_callable(eager("high", priority=1), lambda context=None: "high")
        results = ctx.resolve_all()
        assert results[0].name == "high"
        assert results[1].name == "low"

    def test_resolve_evaluates_lazy_dep(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        ctx.register_callable(lazy("l1"), lambda context=None: "lazy_result")
        res = ctx.resolve("l1")
        assert res.success is True
        assert res.result == "lazy_result"

    def test_resolve_evaluates_eager_dep(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        ctx.register_callable(eager("e1"), lambda context=None: "eager_result")
        res = ctx.resolve("e1")
        assert res.success is True
        assert res.result == "eager_result"

    def test_resolve_caches_result(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        call_count = {"n": 0}

        def counter(context: dict[str, Any] | None = None) -> int:
            call_count["n"] += 1
            return call_count["n"]

        ctx.register_callable(lazy("c1"), counter)
        r1 = ctx.resolve("c1")
        r2 = ctx.resolve("c1")
        assert r1.result == 1
        assert r2.result == 1
        assert r1 is r2

    def test_resolve_missing_callable_returns_failure(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        ctx.register(lazy("l1"))
        res = ctx.resolve("l1")
        assert res.success is False
        assert isinstance(res.error, MissingDependencyError)

    def test_resolve_callable_raises_returns_failure(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        ctx.register_callable(
            lazy("l1"),
            lambda context=None: (_ for _ in ()).throw(ValueError("boom")),
        )
        res = ctx.resolve("l1")
        assert res.success is False
        assert isinstance(res.error, ValueError)

    def test_resolve_passes_heritage_context(self) -> None:
        ctx = DownstreamContext(agent_id="root", heritage={"a": 1})
        received: list[dict[str, Any]] = []
        ctx.register_callable(
            eager("e1", inherits=("a",)),
            lambda context=None: received.append(context),
        )
        results = ctx.resolve_all()
        assert results[0].success is True
        assert received == [{"a": 1}]


# ============================================================================
# TestDownstreamContextSnapshot
# ============================================================================


class TestDownstreamContextSnapshot:
    def test_snapshot_returns_topology_log(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        ctx.register(eager("a")).register(lazy("b"))
        snap = ctx.snapshot()
        assert isinstance(snap, TopologyLog)
        assert snap.root_agent == "root"
        assert snap.eager_deps == ("a",)
        assert snap.lazy_deps == ("b",)

    def test_log_topology_returns_non_empty_string(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        line = ctx.log_topology()
        assert isinstance(line, str)
        assert len(line) > 0

    def test_spawn_creates_child_context(self) -> None:
        parent = DownstreamContext(agent_id="root", heritage={"a": 1})
        child = parent.spawn("child1")
        assert child.parent is parent
        assert child.agent_id == "child1"
        assert child.heritage == {"a": 1}

    def test_spawn_inherits_heritage_not_overrides(self) -> None:
        parent = DownstreamContext(agent_id="root", heritage={"a": 1, "b": 2})
        parent.set_override("b", 3)
        child = parent.spawn("child1")
        assert child.heritage == {"a": 1, "b": 2}

    def test_total_dependencies(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        ctx.register(eager("a")).register(lazy("b"))
        assert ctx.total_dependencies == 2

    def test_eager_count(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        ctx.register(eager("a")).register(lazy("b"))
        assert ctx.eager_count == 1

    def test_lazy_count(self) -> None:
        ctx = DownstreamContext(agent_id="root")
        ctx.register(eager("a")).register(lazy("b"))
        assert ctx.lazy_count == 1


# ============================================================================
# TestAgentGraph
# ============================================================================


class TestAgentGraph:
    def test_resolve_all_resolves_root_and_children(self) -> None:
        root = DownstreamContext(agent_id="root")
        root.register_callable(eager("r1"), lambda context=None: "root_res")

        child = root.spawn("child")
        child.register_callable(eager("c1"), lambda context=None: "child_res")

        graph = AgentGraph(root=root)
        graph.add(child)

        results = graph.resolve_all()
        names = [r.name for r in results]
        assert "r1" in names
        assert "c1" in names

    def test_topology_log_returns_one_line_per_agent(self) -> None:
        root = DownstreamContext(agent_id="root")
        child = root.spawn("child")
        graph = AgentGraph(root=root)
        graph.add(child)
        lines = graph.topology_log()
        assert len(lines) == 2

    def test_agent_count_includes_root(self) -> None:
        root = DownstreamContext(agent_id="root")
        child = root.spawn("child")
        graph = AgentGraph(root=root)
        graph.add(child)
        assert graph.agent_count == 2

    def test_agent_count_root_only(self) -> None:
        root = DownstreamContext(agent_id="root")
        graph = AgentGraph(root=root)
        assert graph.agent_count == 1


# ============================================================================
# TestResolutionResult
# ============================================================================


class TestResolutionResult:
    def test_success_true_sets_result_error_none(self) -> None:
        r = ResolutionResult(name="d1", success=True, result=42)
        assert r.success is True
        assert r.result == 42
        assert r.error is None

    def test_success_false_sets_error_result_none(self) -> None:
        err = ValueError("boom")
        r = ResolutionResult(name="d1", success=False, result=None, error=err)
        assert r.success is False
        assert r.result is None
        assert r.error is err

    def test_heritage_default_empty(self) -> None:
        r = ResolutionResult(name="d1", success=True, result=42)
        assert r.heritage == {}


# ============================================================================
# TestMissingDependencyError
# ============================================================================


class TestMissingDependencyError:
    def test_error_message_includes_dep_name(self) -> None:
        err = MissingDependencyError(dep_name="my_dep", reason="no callable")
        assert "my_dep" in str(err)

    def test_reason_attribute(self) -> None:
        err = MissingDependencyError(dep_name="my_dep", reason="because")
        assert err.reason == "because"

    def test_dep_name_attribute(self) -> None:
        err = MissingDependencyError(dep_name="my_dep")
        assert err.dep_name == "my_dep"

    def test_reason_default_empty(self) -> None:
        err = MissingDependencyError(dep_name="my_dep")
        assert err.reason == ""

    def test_message_without_reason(self) -> None:
        err = MissingDependencyError(dep_name="my_dep")
        assert str(err) == "Missing dependency 'my_dep'"


# ============================================================================
# TestTopologyLog
# ============================================================================


class TestTopologyLog:
    def test_summary_returns_non_empty_string(self) -> None:
        tl = TopologyLog(
            root_agent="root",
            eager_deps=("a",),
            lazy_deps=("b",),
            heritage_keys=("h1",),
            overrides_keys=(),
        )
        assert len(tl.summary()) > 0

    def test_parent_agent_is_none_for_root(self) -> None:
        tl = TopologyLog(
            root_agent="root",
            eager_deps=(),
            lazy_deps=(),
            heritage_keys=(),
            overrides_keys=(),
            parent_agent=None,
        )
        assert tl.parent_agent is None

    def test_summary_includes_parent_when_set(self) -> None:
        tl = TopologyLog(
            root_agent="child",
            eager_deps=(),
            lazy_deps=(),
            heritage_keys=(),
            overrides_keys=(),
            parent_agent="parent",
        )
        assert "parent" in tl.summary()

    def test_frozen(self) -> None:
        tl = TopologyLog(
            root_agent="root",
            eager_deps=(),
            lazy_deps=(),
            heritage_keys=(),
            overrides_keys=(),
        )
        with pytest.raises(AttributeError):
            tl.root_agent = "x"  # type: ignore[misc]
