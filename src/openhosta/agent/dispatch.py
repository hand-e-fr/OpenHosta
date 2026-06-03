"""Capability dispatcher — look-up, route and execute registered capabilities.

DEF-CAP-API-001 — Unified dispatcher API for routed capability execution

The dispatcher uses :class:`CapabilityRegistration` as its data source and
provides dispatch-by-name, route-by-tag, and route-by-type strategies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from openhosta.agent.capability import (
    CapabilityMetadata,
    CapabilityRegistration,
    CapabilityType,
)

# --------------------------------------------------------------------------- #
# DispatchResult
# --------------------------------------------------------------------------- #


@dataclass
class DispatchResult:
    """Encapsulates the outcome of a dispatch call.

    Parameters
    ----------
    success: bool
        ``True`` if the capability was called without raising.
    result: Any
        The return value of the capability (only meaningful when *success*
        is ``True``).
    error: Exception | None
        The caught exception (only meaningful when *success* is ``False``).
    metadata: CapabilityMetadata | None
        The metadata of the dispatched capability, or ``None`` if no
        capability was found.
    """

    success: bool
    result: Any = None
    error: Exception | None = None
    metadata: CapabilityMetadata | None = None


# --------------------------------------------------------------------------- #
# CapabilityDispatcher
# --------------------------------------------------------------------------- #


class CapabilityDispatcher:
    """Look-up, route and execute registered capabilities.

    Parameters
    ----------
    registry: CapabilityRegistration | None
        The registry to query. Defaults to the global singleton.
    """

    def __init__(self, registry: CapabilityRegistration | None = None) -> None:
        self._registry = registry if registry is not None else CapabilityRegistration()

    # ---- dispatch by name ----

    def dispatch(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> DispatchResult:
        """Invoke the capability registered under *name* with *args*/*kwargs*.

        Parameters
        ----------
        name: str
            Capability name.
        *args: Any
            Positional arguments forwarded to the callable.
        **kwargs: Any
            Keyword arguments forwarded to the callable.

        Returns
        -------
        DispatchResult
            Contains ``success``, ``result``, optionally ``error``.

        Examples
        --------
        >>> dispatcher = CapabilityDispatcher()
        >>> result = dispatcher.dispatch("file.read", path="hello.txt")
        >>> if result.success:
        ...     print(result.result)
        """
        lookup = self._registry.find_by_name(name)
        if lookup is None:
            return DispatchResult(
                success=False,
                error=KeyError(f"Capability '{name}' not found in registry"),
                metadata=None,
            )

        func, metadata = lookup
        try:
            result = func(*args, **kwargs)
            return DispatchResult(success=True, result=result, metadata=metadata)
        except Exception as exc:  # noqa: BLE001 – we capture everything
            return DispatchResult(success=False, error=exc, metadata=metadata)

    # ---- route by type ----

    def route_by_type(
        self,
        capacity_type: CapabilityType,
        *args: Any,
        **kwargs: Any,
    ) -> list[DispatchResult]:
        """Execute *all* capabilities matching *capacity_type*.

        Parameters
        ----------
        capacity_type: CapabilityType
            The type to filter on.
        *args: Any
            Positional arguments forwarded to each callable.
        **kwargs: Any
            Keyword arguments forwarded to each callable.

        Returns
        -------
        list[DispatchResult]
            One result per matching capability, sorted by priority
            (ascending).
        """
        matches = self._registry.find_by_type(capacity_type)
        ranked = sorted(matches, key=lambda entry: entry[1].priority)
        results: list[DispatchResult] = []
        for func, metadata in ranked:
            try:
                result = func(*args, **kwargs)
                results.append(DispatchResult(success=True, result=result, metadata=metadata))
            except Exception as exc:  # noqa: BLE001
                results.append(DispatchResult(success=False, error=exc, metadata=metadata))
        return results

    # ---- route by tag ----

    def route_by_tag(
        self,
        tag: str,
        *args: Any,
        **kwargs: Any,
    ) -> list[DispatchResult]:
        """Execute *all* capabilities whose tags contain *tag*.

        Parameters are analogous to :meth:`route_by_type`.

        Returns
        -------
        list[DispatchResult]
            One result per matching capability, sorted by priority.
        """
        matches = self._registry.find_by_tag(tag)
        ranked = sorted(matches, key=lambda entry: entry[1].priority)
        results: list[DispatchResult] = []
        for func, metadata in ranked:
            try:
                result = func(*args, **kwargs)
                results.append(DispatchResult(success=True, result=result, metadata=metadata))
            except Exception as exc:  # noqa: BLE001
                results.append(DispatchResult(success=False, error=exc, metadata=metadata))
        return results

    # ---- registry access ----

    @property
    def registry(self) -> CapabilityRegistration:
        """The underlying :class:`CapabilityRegistration` instance."""
        return self._registry

    def capability_count(self) -> int:
        """Return the number of registered capabilities."""
        return self._registry.count

    def list_capabilities(self) -> list[CapabilityMetadata]:
        """Return the metadata of every registered capability."""
        return [entry[1] for entry in self._registry.list_all()]
