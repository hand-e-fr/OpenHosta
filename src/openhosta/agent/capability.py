"""Capability decorators and auto-registration registry for OpenHosta V5.

DEF-CAP-001 — Capability definition via decorators
DEF-CAP-API-001 — Unified dispatcher API for routed capability execution

Decorators
----------
- @tool(name, description, tags)    — deterministic, side-effect capable routine
- @infer(name, description, tags)   — LLM-based probabilistic capability
- @playbook(name, description, tags) — multi-step orchestrated workflow
- @planner(name, description, tags)  — goal decomposition / planning capability
- @router(name, description, tags)   — routing decision capability

Registry
--------
CapabilityRegistration — global singleton that collects every decorated
capability and exposes lookup by name, type, or tag.

Inference delegation
--------------------
When @infer/@planner/@router decorate a stub function (body is only `...`),
the decorator wraps the callable so that invocation delegates to the
InferenceEngine (LLM backend). Non-stub functions execute directly.
"""

from __future__ import annotations

import functools
import inspect
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

# --------------------------------------------------------------------------- #
# CapabilityType enum
# --------------------------------------------------------------------------- #


class CapabilityType(Enum):
    """Categorisation d'une capacité."""

    TOOL = auto()
    """Routine déterministe, potentiellement avec effets de bord."""

    INFERENCE = auto()
    """Capacité probabiliste basée sur un LLM."""

    PLAYBOOK = auto()
    """Workflow orchestré multi-étapes."""

    PLANNER = auto()
    """Décomposition de but / planification."""

    ROUTER = auto()
    """Capacité de décision de routage."""


# --------------------------------------------------------------------------- #
# CapabilityMetadata
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class CapabilityMetadata:
    """Metadata attached to any registered capability.

    Parameters
    ----------
    name: str
        Unique capability identifier (dot-notation encouraged).
        Defaults to the decorated function's ``__name__``.
    capacity_type: CapabilityType
        Category of this capability.
    description: str
        Human-readable one-liner (first line of docstring by default).
    long_description: str
        Full docstring enriched with the function signature and type
        annotations.  Used by the InferenceEngine to build prompts.
    tags: tuple[str, ...]
        Arbitrary search tags (frozen tuple for hashability).
    priority: int
        Scheduling priority (lower = more urgent). Default ``0``.
    requires_async: bool
        ``True`` when the callable expects ``async def`` signature.
    """

    name: str
    capacity_type: CapabilityType
    description: str = ""
    long_description: str = ""
    tags: tuple[str, ...] = ()
    priority: int = 0
    requires_async: bool = False

    @property
    def tag_set(self) -> set[str]:
        """Tags as a set for efficient membership testing."""
        return set(self.tags)


# --------------------------------------------------------------------------- #
# CapabilityRegistration (singleton registry)
# --------------------------------------------------------------------------- #


class CapabilityRegistration:
    """Global registry for decorated capabilities.

    Every @tool / @infer / @playbook / @planner / @router decorator
    registers the target callable here automatically.

    The registry is thread-safe for single-writer / multi-reader workloads.
    """

    _instance: CapabilityRegistration | None = None
    _store: dict[str, tuple[Callable[..., Any], CapabilityMetadata]]

    def __new__(cls) -> CapabilityRegistration:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._store = {}
        return cls._instance

    # ---- public API ----

    def register(
        self,
        func: Callable[..., Any],
        metadata: CapabilityMetadata,
    ) -> Callable[..., Any]:
        """Register *func* under *metadata.name*.

        Raises
        ------
        ValueError
            If *metadata.name* is already registered.
        """
        if metadata.name in self._store:
            old_func, old_meta = self._store[metadata.name]
            raise ValueError(
                f"Capability '{metadata.name}' already registered "
                f"(was: {old_func.__qualname__}, type={old_meta.capacity_type.name})"
            )
        self._store[metadata.name] = (func, metadata)
        return func

    def get(self, name: str) -> tuple[Callable[..., Any], CapabilityMetadata]:
        """Retrieve a capability by its name.

        Raises
        ------
        KeyError
            If *name* is not registered.
        """
        if name not in self._store:
            raise KeyError(f"Capability '{name}' not found in registry")
        return self._store[name]

    def find_by_name(self, name: str) -> tuple[Callable[..., Any], CapabilityMetadata] | None:
        """Retrieve *name* or ``None`` if absent (non-raising variant)."""
        try:
            return self.get(name)
        except KeyError:
            return None

    def find_by_type(
        self, capacity_type: CapabilityType
    ) -> list[tuple[Callable[..., Any], CapabilityMetadata]]:
        """Return all capabilities matching *capacity_type*."""
        return [
            entry for entry in self._store.values() if entry[1].capacity_type == capacity_type
        ]

    def find_by_tag(self, tag: str) -> list[tuple[Callable[..., Any], CapabilityMetadata]]:
        """Return all capabilities whose tags contain *tag*."""
        return [entry for entry in self._store.values() if tag in entry[1].tag_set]

    def list_all(self) -> list[tuple[Callable[..., Any], CapabilityMetadata]]:
        """Return every registered capability (order not guaranteed)."""
        return list(self._store.values())

    def clear(self) -> None:
        """Remove all registered capabilities. Useful for test isolation."""
        self._store.clear()

    @property
    def count(self) -> int:
        """Number of registered capabilities."""
        return len(self._store)


# --------------------------------------------------------------------------- #
# Decorators
# --------------------------------------------------------------------------- #

# Single global registry instance
_registry = CapabilityRegistration()


# --------------------------------------------------------------------------- #
# Metadata resolution helpers
# --------------------------------------------------------------------------- #


def _extract_first_line(docstring: str | None) -> str:
    """Return the first non-empty line of a docstring."""
    if not docstring:
        return ""
    lines = docstring.strip().splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def _build_signature_summary(func: Callable[..., Any]) -> str:
    """Build a human-readable signature with type annotations.

    Example: ``func(msg: str, count: int = 10) -> str``
    """
    try:
        sig = inspect.signature(func)
        return f"{func.__name__}{sig}"
    except (ValueError, TypeError):
        return func.__name__


def _build_long_description(func: Callable[..., Any]) -> str:
    """Build the long description from docstring + signature.

    Convention V5 : la description longue combine la docstring complète
    et le prototype annoté pour alimenter les prompts de l'InferenceEngine.
    """
    parts: list[str] = []

    sig_summary = _build_signature_summary(func)
    parts.append(f"**Signature:** `{sig_summary}`")

    doc = (func.__doc__ or "").strip()
    if doc:
        parts.append(f"\n**Docstring:**\n{doc}")

    return "\n".join(parts)


def _resolve_metadata(
    func: Callable[..., Any],
    capacity_type: CapabilityType,
    name: str | None = None,
    description: str | None = None,
    tags: list[str] | tuple[str, ...] | None = None,
    priority: int = 0,
    requires_async: bool = False,
) -> CapabilityMetadata:
    """Resolve capability metadata from the decorated function.

    Convention V5 :
    - ``name`` dérive de ``func.__name__`` si non fourni
    - ``description`` courte = première ligne de la docstring
    - ``long_description`` = docstring complète + signature annotée
    """
    tags_tuple: tuple[str, ...] = tuple(tags) if tags is not None else ()

    resolved_name = name if name is not None else func.__name__
    docstring = (func.__doc__ or "").strip()
    resolved_description = (
        description if description is not None
        else _extract_first_line(docstring)
    )
    long_desc = _build_long_description(func)

    return CapabilityMetadata(
        name=resolved_name,
        capacity_type=capacity_type,
        description=resolved_description,
        long_description=long_desc,
        tags=tags_tuple,
        priority=priority,
        requires_async=requires_async,
    )


def _make_decorator(capacity_type: CapabilityType) -> Callable[..., Callable[..., Any]]:
    """Factory that returns a decorator for *capacity_type*.

    Convention V5 : ``name`` et ``description`` sont optionnels.
    S'ils ne sont pas fournis, ils sont dérivés de la fonction décorée :
    - ``name`` ← ``func.__name__``
    - ``description`` ← première ligne de la docstring
    - ``long_description`` ← docstring complète + signature annotée
    """

    def decorator(
        *,
        name: str | None = None,
        description: str | None = None,
        tags: list[str] | tuple[str, ...] | None = None,
        priority: int = 0,
        requires_async: bool = False,
    ) -> Callable[..., Callable[..., Any]]:
        def inner(func: Callable[..., Any]) -> Callable[..., Any]:
            meta = _resolve_metadata(
                func, capacity_type, name, description, tags, priority, requires_async
            )
            # Attach metadata directly without functools.wraps to avoid
            # creating a wrapper loop (func.__wrapped__ = func).
            func._capability = meta  # type: ignore[attr-defined]
            _registry.register(func, meta)
            return func

        return inner

    return decorator


def _wrap_inference(
    func: Callable[..., Any],
    meta: CapabilityMetadata,
) -> Callable[..., Any]:
    """Wrap a stub capability to delegate to InferenceEngine on invocation.

    When the decorated function is a stub (body is only `...` or `pass`),
    this wrapper intercepts calls and delegates to the LLM backend via
    the InferenceEngine. Non-stub functions are returned unchanged.

    Parameters
    ----------
    func: Callable[..., Any]
        The decorated callable.
    meta: CapabilityMetadata
        The capability metadata.

    Returns
    -------
    Callable[..., Any]
        Either the original function (non-stub) or an inference wrapper.
    """
    from openhosta.agent.inference import is_stub, execute_inference

    if not is_stub(func):
        return func

    @functools.wraps(func)
    def _infer_wrapper(*args: Any, **kwargs: Any) -> Any:
        # Explicit is better than implicit: backend must be injected.
        # Inside Agent.get(), this is handled via _backend kwarg.
        # Standalone, the user should call model.infer(func, ...).
        backend = kwargs.pop("_backend", None)
        if backend is None:
            # Fallback to global config (Agent.recruit() sets this)
            from openhosta.agent._config import get_default_backend
            backend = get_default_backend()

        if backend is None:
            raise NotImplementedError(
                f"This capability '{meta.name}' is a stub and requires a backend. "
                f"Use model.infer({func.__name__}, ...) or Agent.get(...) to execute it."
            )
        result = execute_inference(func, meta, backend, *args, **kwargs)
        if not result.success:
            raise RuntimeError(
                f"Inference failed for '{meta.name}': {result.error}"
            ) from result.error
        return result.value

    return _infer_wrapper


def tool(
    *,
    name: str | None = None,
    description: str | None = None,
    tags: list[str] | tuple[str, ...] | None = None,
    priority: int = 0,
    requires_async: bool = False,
) -> Callable[..., Callable[..., Any]]:
    """Mark a function as a **tool** capability (deterministic routine).

    Convention V5 : ``name`` et ``description`` sont optionnels.
    S'ils ne sont pas fournis, ils sont dérivés de la fonction décorée.

    Example
    -------
    >>> @tool(tags=["files"])
    ... def read_file(path: str) -> str:
    ...     \"\"\"Read the file at *path\"\"\"
    ...     return Path(path).read_text()
    """
    return _make_decorator(CapabilityType.TOOL)(
        name=name,
        description=description,
        tags=tags,
        priority=priority,
        requires_async=requires_async,
    )


def infer(
    *,
    name: str | None = None,
    description: str | None = None,
    tags: list[str] | tuple[str, ...] | None = None,
    priority: int = 0,
    requires_async: bool = False,
) -> Callable[..., Callable[..., Any]]:
    """Mark a function as an **inference** capability (LLM-driven).

    If the decorated function is a stub (body is only `...`), invocation
    delegates to the InferenceEngine (LLM backend). Non-stub functions
    execute directly.

    Convention V5 : ``name`` et ``description`` sont optionnels.
    """

    def inner(func: Callable[..., Any]) -> Callable[..., Any]:
        meta = _resolve_metadata(
            func, CapabilityType.INFERENCE, name, description, tags, priority, requires_async
        )
        # Attach metadata directly without functools.wraps to avoid
        # creating a wrapper loop (func.__wrapped__ = func).
        func._capability = meta  # type: ignore[attr-defined]
        # Wrap stubs with inference delegation
        wrapped = _wrap_inference(func, meta)
        _registry.register(wrapped, meta)
        return wrapped

    return inner


def playbook(
    *,
    name: str | None = None,
    description: str | None = None,
    tags: list[str] | tuple[str, ...] | None = None,
    priority: int = 0,
    requires_async: bool = False,
) -> Callable[..., Callable[..., Any]]:
    """Mark a function as a **playbook** capability (multi-step workflow).

    Convention V5 : ``name`` et ``description`` sont optionnels.
    """
    return _make_decorator(CapabilityType.PLAYBOOK)(
        name=name,
        description=description,
        tags=tags,
        priority=priority,
        requires_async=requires_async,
    )


def planner(
    *,
    name: str | None = None,
    description: str | None = None,
    tags: list[str] | tuple[str, ...] | None = None,
    priority: int = 0,
    requires_async: bool = False,
) -> Callable[..., Callable[..., Any]]:
    """Mark a function as a **planner** capability (goal decomposition).

    If the decorated function is a stub (body is only `...`), invocation
    delegates to the InferenceEngine (LLM backend). Non-stub functions
    execute directly.

    Convention V5 : ``name`` et ``description`` sont optionnels.
    """

    def inner(func: Callable[..., Any]) -> Callable[..., Any]:
        meta = _resolve_metadata(
            func, CapabilityType.PLANNER, name, description, tags, priority, requires_async
        )
        # Attach metadata directly without functools.wraps to avoid
        # creating a wrapper loop (func.__wrapped__ = func).
        func._capability = meta  # type: ignore[attr-defined]
        wrapped = _wrap_inference(func, meta)
        _registry.register(wrapped, meta)
        return wrapped

    return inner


def router(
    *,
    name: str | None = None,
    description: str | None = None,
    tags: list[str] | tuple[str, ...] | None = None,
    priority: int = 0,
    requires_async: bool = False,
) -> Callable[..., Callable[..., Any]]:
    """Mark a function as a **router** capability (routing decision).

    If the decorated function is a stub (body is only `...`), invocation
    delegates to the InferenceEngine (LLM backend). Non-stub functions
    execute directly.

    Convention V5 : ``name`` et ``description`` sont optionnels.
    """

    def inner(func: Callable[..., Any]) -> Callable[..., Any]:
        meta = _resolve_metadata(
            func, CapabilityType.ROUTER, name, description, tags, priority, requires_async
        )
        # Attach metadata directly without functools.wraps to avoid
        # creating a wrapper loop (func.__wrapped__ = func).
        func._capability = meta  # type: ignore[attr-defined]
        wrapped = _wrap_inference(func, meta)
        _registry.register(wrapped, meta)
        return wrapped

    return inner
