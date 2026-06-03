"""Semantic LLM backend for guarded type resolution.

Provides an injectable backend that delegates casting to an LLM when
heuristic parsing is insufficient. Currently a stub that always returns
failure; wire in a real LLM client to activate.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .primitives import CastingResult


class LlmiSemanticBackend:
    """Stub semantic backend — returns failure until wired to a real LLM client."""

    def resolve(self, value: str, target_type: type) -> "CastingResult":
        """Attempt semantic resolution via LLM.

        Args:
            value: The raw input string to cast.
            target_type: The Python type to cast to.

        Returns:
            A CastingResult.failure() for now; replace body with real LLM call.
        """
        from .primitives import CastingResult

        return CastingResult.failure(
            value,
            error_message=f"Semantic backend not wired: cannot cast {value!r} to {target_type.__name__}",
        )
