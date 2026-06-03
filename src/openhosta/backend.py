from __future__ import annotations

import functools
from dataclasses import dataclass, field
from typing import Any
from collections.abc import Callable


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

    def infer(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute inference for a decorated function using this backend.

        Explicit is better than implicit: use ``model.infer(func, ...)``
        instead of calling the stub function directly.

        Parameters
        ----------
        func: Callable
            A function decorated with ``@infer``, ``@planner``, or ``@router``.
        *args: Any
            Positional arguments forwarded to the inference engine.
        **kwargs: Any
            Keyword arguments forwarded to the inference engine.

        Returns
        -------
        Any
            The parsed result from the LLM backend.

        Raises
        ------
        RuntimeError
            If inference fails or the function is not a registered capability.
        """
        meta = getattr(func, "_capability", None)
        if meta is None:
            raise ValueError(
                f"Function '{func.__name__}' is not a registered capability. "
                f"Decorate it with @infer, @planner, or @router first."
            )

        from openhosta.agent.inference import execute_inference  # noqa: PLC2701

        result = execute_inference(func, meta, self, *args, **kwargs)
        if not result.success:
            raise RuntimeError(
                f"Inference failed for '{meta.name}': {result.error}"
            ) from result.error
        return result.value

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
