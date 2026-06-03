from __future__ import annotations

import functools
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class BackendModel:
    """Describes a single LLM backend configuration."""

    provider: str
    model_name: str
    base_url: str
    api_key: str = ""
    tags: tuple[str, ...] = ()
    priority: int = 0

    def compile(self) -> Any:
        """Class decorator that marks an agent class as compiled against this backend.

        Returns the class unchanged, preserving its identity.
        """

        def decorator(cls: type) -> type:
            cls._backend = self  # type: ignore[attr-defined]
            return cls

        return decorator

    @property
    def tag_set(self) -> set[str]:
        return set(self.tags)


class BackendSelector:
    """Resolves the best backend from a list of candidates."""

    def __init__(self, candidates: list[BackendModel]) -> None:
        if not candidates:
            raise ValueError("candidates must not be empty")
        self.candidates = list(candidates)

    def resolve(self, constraints: dict | None = None) -> BackendModel:
        """Return the best matching backend.

        By default (no constraints), returns the first candidate.
        When constraints specify a tag, returns the first candidate
        whose tag_set intersects with the requested tags.
        """
        if constraints is None:
            return self.candidates[0]

        requested_tags: set[str] = set(constraints.get("tags", []))
        if not requested_tags:
            return self.candidates[0]

        for candidate in self.candidates:
            if candidate.tag_set & requested_tags:
                return candidate

        return self.candidates[0]
