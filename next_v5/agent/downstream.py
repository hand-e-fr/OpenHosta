"""Downstream dependency management and heritage context propagation.

REQ-DOWNSTREAM-001 — Dependency graph with lazy/eager evaluation and
                     heritage context inheritance through agent hierarchies

This module provides the machinery to express and resolve inter-agent
dependencies:

1. **Dependency** — declarative node carrying a callable, mode (``lazy`` /
   ``eager``) and an ``inherits`` set that selects which heritage keys
   are inherited from the parent context.

2. **DownstreamContext** — mutable container that owns the dependency
   graph, resolves it in topological order, propagates heritage data
   down the chain and logs the resulting topology on activation.

3. **lazy(**), **eager(**)** — convenience constructors for :class:`Dependency`.

4. **MissingDependencyError** — raised when a dependency cannot be
   resolved at the required point.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #

logger: logging.Logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# MissingDependencyError
# --------------------------------------------------------------------------- #


class MissingDependencyError(Exception):
    """Raised when a downstream dependency cannot be satisfied.

    Parameters
    ----------
    dep_name: str
        The missing dependency name.
    reason: str
        Human-readable explanation.
    """

    def __init__(self, dep_name: str, reason: str = "") -> None:
        message = f"Missing dependency '{dep_name}'"
        if reason:
            message = f"{message}: {reason}"
        super().__init__(message)
        self.dep_name = dep_name
        self.reason = reason


# --------------------------------------------------------------------------- #
# DependencyMode
# --------------------------------------------------------------------------- #


class DependencyMode(Enum):
    """Evaluation strategy for a dependency."""

    LAZY = auto()
    """Evaluated only when explicitly requested (on-demand)."""

    EAGER = auto()
    """Evaluated automatically during graph resolution (topological order)."""


# --------------------------------------------------------------------------- #
# Dependency
# --------------------------------------------------------------------------- #


@dataclass
class Dependency:
    """Single downstream dependency node.

    Parameters
    ----------
    name: str
        Uniquely scoped identifier (e.g. ``"pipeline.preprocessing"``).
    mode: DependencyMode
        Whether this dependency is evaluated lazily (on demand) or
        eagerly (during topological resolution).
    inherits: tuple[str, ...]
        Keys from the parent :class:`DownstreamContext` ``heritage`` dict
        that should be inherited by this dependency's child context.
        Empty tuple (default) means inherit nothing.
    tag: str
        Optional human-readable category tag (e.g. ``"data"`` or
        ``"compute"``).
    priority: int
        Scheduling priority (lower = evaluated first; default 0).
    """

    name: str
    mode: DependencyMode
    inherits: tuple[str, ...] = ()
    tag: str = ""
    priority: int = 0

    @property
    def is_lazy(self) -> bool:
        """``True`` when this dependency is evaluated on-demand."""
        return self.mode == DependencyMode.LAZY

    @property
    def is_eager(self) -> bool:
        """``True`` when this dependency is evaluated in resolution."""
        return self.mode == DependencyMode.EAGER


# --------------------------------------------------------------------------- #
# Convenience constructors
# --------------------------------------------------------------------------- #


def lazy(
    name: str,
    *,
    inherits: tuple[str, ...] | list[str] | None = None,
    tag: str = "",
    priority: int = 0,
) -> Dependency:
    """Construct a **lazy** dependency.

    The dependency will only be resolved when explicitly requested
    via ``DownstreamContext.resolve(name)``.

    Parameters
    ----------
    name: str
        Dependency identifier.
    inherits: tuple[str, ...] | list[str] | None
        Heritage keys to inherit from parent.
    tag: str
        Optional category tag.
    priority: int
        Scheduling priority (ignored for lazy deps, kept for API symmetry).

    Returns
    -------
    Dependency
    """
    inherits_tuple: tuple[str, ...]
    if inherits is None:
        inherits_tuple = ()
    elif isinstance(inherits, list):
        inherits_tuple = tuple(inherits)
    else:
        inherits_tuple = inherits

    return Dependency(
        name=name,
        mode=DependencyMode.LAZY,
        inherits=inherits_tuple,
        tag=tag,
        priority=priority,
    )


def eager(
    name: str,
    *,
    inherits: tuple[str, ...] | list[str] | None = None,
    tag: str = "",
    priority: int = 0,
) -> Dependency:
    """Construct an **eager** dependency.

    The dependency will be resolved automatically during
    ``DownstreamContext.resolve_all()``.

    Parameters
    ----------
    name: str
        Dependency identifier.
    inherits: tuple[str, ...] | list[str] | None
        Heritage keys to inherit from parent.
    tag: str
        Optional category tag.
    priority: int
        Scheduling priority (lower = evaluated first).

    Returns
    -------
    Dependency
    """
    inherits_tuple: tuple[str, ...]
    if inherits is None:
        inherits_tuple = ()
    elif isinstance(inherits, list):
        inherits_tuple = tuple(inherits)
    else:
        inherits_tuple = inherits

    return Dependency(
        name=name,
        mode=DependencyMode.EAGER,
        inherits=inherits_tuple,
        tag=tag,
        priority=priority,
    )


# --------------------------------------------------------------------------- #
# ResolutionResult — encapsulates outcome of a single dep resolution
# --------------------------------------------------------------------------- #


@dataclass
class ResolutionResult:
    """Outcome of resolving one dependency.

    Parameters
    ----------
    name: str
        The dependency name.
    success: bool
        ``True`` when the callable returned without raising.
    result: Any
        The return value (only meaningful when *success* is ``True``).
    error: Exception | None
        The raised exception (only meaningful when *success* is ``False``).
    heritage: dict[str, Any]
        The heritage context that was passed to the callable.
    """

    name: str
    success: bool
    result: Any
    error: Exception | None = None
    heritage: dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# TopologyLog — immutable record emitted on recruitment / resolution
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class TopologyLog:
    """Snapshot of the agent graph topology at resolution time.

    Parameters
    ----------
    root_agent: str
        The agent ID that owns this context.
    eager_deps: tuple[str, ...]
        Names of eager dependencies in evaluation order.
    lazy_deps: tuple[str, ...]
        Names of registered lazy dependencies (unresolved).
    heritage_keys: tuple[str, ...]
        Keys present in the heritage dict at snapshot time.
    overrides_keys: tuple[str, ...]
        Keys present in the overrides dict at snapshot time.
    parent_agent: str | None
        Parent agent ID (``None`` for root agents).
    """

    root_agent: str
    eager_deps: tuple[str, ...]
    lazy_deps: tuple[str, ...]
    heritage_keys: tuple[str, ...]
    overrides_keys: tuple[str, ...]
    parent_agent: str | None = None

    def summary(self) -> str:
        """Return a one-line human-readable topology summary."""
        parent = f" (parent: {self.parent_agent})" if self.parent_agent else ""
        return (
            f"[{self.root_agent}]{parent} "
            f"eager={len(self.eager_deps)} "
            f"lazy={len(self.lazy_deps)} "
            f"heritage={len(self.heritage_keys)}"
        )


# --------------------------------------------------------------------------- #
# DownstreamContext — central container
# --------------------------------------------------------------------------- #


@dataclass
class DownstreamContext:
    """Manages inter-agent dependencies, heritage propagation and overrides.

    An agent registers its downstream dependencies here.  During
    ``resolve_all()``, eager dependencies are evaluated in priority order
    while lazy dependencies remain available for on-demand resolution.

    Heritage data flows from parent → child.  Overrides allow the parent
    to inject values that mask inherited heritage keys.

    Parameters
    ----------
    agent_id: str
        The agent that owns this context.
    parent: DownstreamContext | None
        Optional parent context from which heritage is inherited.
    heritage: dict[str, Any] | None
        Key-value pairs inherited from upstream. Merged with parent
        heritage automatically. Defaults to ``{} `` (normalised in
        ``__post_init__``).
    overrides: dict[str, Any] | None
        Explicit overrides that replace heritage values for downstream
        children. Defaults to ``{}`` (normalised in ``__post_init__``).
    dependencies: list[Dependency] | None
        Pre-registered dependencies. Defaults to ``[]`` (normalised
        in ``__post_init__``).
    """

    agent_id: str
    parent: DownstreamContext | None = None
    # These fields are normalised (never None) by __post_init__
    heritage: dict[str, Any] = field(default_factory=dict)
    overrides: dict[str, Any] = field(default_factory=dict)
    dependencies: list[Dependency] = field(default_factory=list)

    # ---- internal mutable state ----
    _registry: dict[str, Any] = field(default_factory=dict, repr=False)
    _results: dict[str, ResolutionResult] = field(default_factory=dict, repr=False)

    # ---- post-init: merge parent heritage ----
    def __post_init__(self) -> None:
        if self.parent is not None:
            self.heritage = {**self.parent.heritage, **self.heritage}

    # ---- dependency management ----

    def register(self, dep: Dependency) -> DownstreamContext:
        """Add *dep* to this context's dependency list.

        Returns self for chaining.

        Raises
        ------
        ValueError
            If a dependency with the same ``name`` is already registered.
        """
        if any(d.name == dep.name for d in self.dependencies):
            raise ValueError(f"Duplicate dependency '{dep.name}'")
        self.dependencies.append(dep)
        return self

    def register_callable(self, dep: Dependency, func: Any) -> DownstreamContext:
        """Register a dependency **and** its callable in one call.

        Returns self for chaining.
        """
        self.register(dep)
        self._registry[dep.name] = func
        return self

    def get_dependency(self, name: str) -> Dependency:
        """Retrieve a dependency by name.

        Raises
        ------
        KeyError
            If *name* is not found.
        """
        for dep in self.dependencies:
            if dep.name == name:
                return dep
        raise KeyError(f"Dependency '{name}' not found")

    def eager_deps(self) -> list[Dependency]:
        """Return all eager dependencies sorted by (priority, registration order)."""
        eager = [d for d in self.dependencies if d.is_eager]
        eager.sort(key=lambda d: d.priority)
        return eager

    def lazy_deps(self) -> list[Dependency]:
        """Return all lazy dependencies (sorted by priority for consistency)."""
        lazy = [d for d in self.dependencies if d.is_lazy]
        lazy.sort(key=lambda d: d.priority)
        return lazy

    # ---- heritage & overrides ----

    def get_heritage(self, key: str, default: Any = None) -> Any:
        """Look up *key* with overrides taking precedence over heritage.

        Returns *default* if the key is absent from both dicts.
        """
        if key in self.overrides:
            return self.overrides[key]
        return self.heritage.get(key, default)

    def set_override(self, key: str, value: Any) -> None:
        """Set an explicit override for *key*."""
        self.overrides[key] = value

    def effective_heritage(self) -> dict[str, Any]:
        """Return the merged heritage view (overrides layered on top)."""
        merged: dict[str, Any] = dict(self.heritage)
        merged.update(self.overrides)
        return merged

    def child_heritage(self, dep: Dependency) -> dict[str, Any]:
        """Build a heritage dict for a child context of *dep*.

        Only keys listed in ``dep.inherits`` are forwarded from this
        context's effective heritage.
        """
        effective = self.effective_heritage()
        if not dep.inherits:
            return {}
        return {k: effective[k] for k in dep.inherits if k in effective}

    # ---- resolution ----

    def resolve_all(self) -> list[ResolutionResult]:
        """Evaluate all **eager** dependencies in priority order.

        Returns
        -------
        list[ResolutionResult]
            One result per eager dependency in evaluation order.
        """
        results: list[ResolutionResult] = []
        for dep in self.eager_deps():
            results.append(self._resolve_one(dep))
        return results

    def resolve(self, name: str) -> ResolutionResult:
        """Evaluate a single (lazy or eager) dependency by name.

        If the dependency was previously resolved, returns the cached
        result.

        Raises
        ------
        KeyError
            If *name* is not registered.
        MissingDependencyError
            If no callable is registered under *name*.
        """
        dep = self.get_dependency(name)
        if name in self._results:
            return self._results[name]
        result = self._resolve_one(dep)
        self._results[name] = result
        return result

    def _resolve_one(self, dep: Dependency) -> ResolutionResult:
        """Internal: execute one dependency callable with heritage context."""
        if dep.name not in self._registry:
            err = MissingDependencyError(
                dep.name,
                f"No callable registered for {dep.mode.name.lower()} dependency",
            )
            return ResolutionResult(
                name=dep.name,
                success=False,
                result=None,
                error=err,
                heritage=self.child_heritage(dep),
            )

        child_ctx = self.child_heritage(dep)
        func = self._registry[dep.name]
        try:
            result = func(context=child_ctx)
            return ResolutionResult(
                name=dep.name,
                success=True,
                result=result,
                heritage=child_ctx,
            )
        except Exception as e:  # noqa: BLE001
            return ResolutionResult(
                name=dep.name,
                success=False,
                result=None,
                error=e,
                heritage=child_ctx,
            )

    # ---- topology snapshot ----

    def snapshot(self) -> TopologyLog:
        """Return an immutable snapshot of the current graph topology."""
        return TopologyLog(
            root_agent=self.agent_id,
            eager_deps=tuple(d.name for d in self.eager_deps()),
            lazy_deps=tuple(d.name for d in self.lazy_deps()),
            heritage_keys=tuple(sorted(self.heritage.keys())),
            overrides_keys=tuple(sorted(self.overrides.keys())),
            parent_agent=self.parent.agent_id if self.parent else None,
        )

    @property
    def total_dependencies(self) -> int:
        """Total number of registered dependencies."""
        return len(self.dependencies)

    @property
    def eager_count(self) -> int:
        """Number of eager dependencies."""
        return sum(1 for d in self.dependencies if d.is_eager)

    @property
    def lazy_count(self) -> int:
        """Number of lazy dependencies."""
        return sum(1 for d in self.dependencies if d.is_lazy)

    def log_topology(self) -> str:
        """Log the topology summary and return it.

        Intended to be called on recruitment or resolve_all().
        """
        topo = self.snapshot()
        summary = topo.summary()
        logger.info("downstream topology: %s", summary)
        return summary

    # ---- child context creation ----

    def spawn(self, agent_id: str) -> DownstreamContext:
        """Create a child DownstreamContext under this one.

        The child inherits all heritage data (minus overrides from
        this level — overrides are local to the owner).
        """
        return DownstreamContext(
            agent_id=agent_id,
            parent=self,
            heritage={},  # child merges with parent in __post_init__
        )


# --------------------------------------------------------------------------- #
# AgentGraph — lightweight graph of interconnected DownstreamContexts
# --------------------------------------------------------------------------- #


@dataclass
class AgentGraph:
    """Simple DAG of agent contexts.

    Parameters
    ----------
    root: DownstreamContext
        The root agent context.
    """

    root: DownstreamContext
    _children: dict[str, DownstreamContext] = field(default_factory=dict, repr=False)

    def add(self, ctx: DownstreamContext) -> AgentGraph:
        """Add a context to the graph. Returns self for chaining."""
        self._children[ctx.agent_id] = ctx
        return self

    def resolve_all(self) -> list[ResolutionResult]:
        """Resolve eager deps for root, then for every child (BFS order)."""
        all_results: list[ResolutionResult] = []
        queue = [self.root]
        while queue:
            node = queue.pop(0)
            all_results.extend(node.resolve_all())
            # children are those contexts whose parent is this node
            for child in self._children.values():
                if child.parent is node:
                    queue.append(child)
        return all_results

    def topology_log(self) -> list[str]:
        """Return topology summary lines for every agent in the graph."""
        lines = [self.root.log_topology()]
        for ctx in self._children.values():
            lines.append(ctx.log_topology())
        return lines

    @property
    def agent_count(self) -> int:
        """Total agents (root + children)."""
        return len(self._children) + 1
