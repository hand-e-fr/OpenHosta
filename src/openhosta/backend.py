from __future__ import annotations

import functools
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING
from collections.abc import Callable

from openhosta.agent.inference import execute_inference

if TYPE_CHECKING:
    from openhosta.agent.capability import CapabilityMetadata


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

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Guard against misuse: BackendModel is NOT a decorator.

        If someone writes ``@model(...)`` they get a clear error redirecting
        them to the correct decorator syntax ``@model.infer(...)``.

        Raises
        ------
        TypeError
            Always – ``BackendModel`` instances must not be called directly.
        """
        # Binding misuse: @model(tags=...)
        if not args and any(k in kwargs for k in ("tags", "priority")):
            raise TypeError(
                "BackendModel is not a decorator. "
                "Use ``@model.infer(tags=[...])`` as the decorator, "
                "not ``@model(tags=[...])``. "
                "See: model.infer(func, ...) for standalone inference."
            )

        # Execution misuse: model(42) or model(func, ...)
        if args:
            target = getattr(args[0], "__name__", repr(args[0]))
            raise TypeError(
                f"BackendModel is not callable with positional arguments. "
                f"Did you mean ``model.infer({target}, ...)`` ?"
            )

        raise TypeError(
            "BackendModel is not callable. "
            "Use ``model.infer(func, ...)`` for standalone inference, "
            "or ``agent.get(msg)`` inside an Agent session."
        )

    # ------------------------------------------------------------------ #
    # Infer as decorator: @model.infer(tags=[...])
    # ------------------------------------------------------------------ #

    def infer(self, *args: Any, **kwargs: Any) -> Any:
        """Dual-mode: decorator binding or direct inference execution.

        Decorator binding (returns a decorator):
            @model.infer(tags=["lang"])
            def translate(text: str) -> str: ...

        Direct execution:
            model.infer(my_func, arg1, key=value)
        """
        from openhosta.agent.capability import CapabilityMetadata, CapabilityType

        # Decorator binding: @model.infer(tags=[...])
        if not args and any(k in kwargs for k in ("tags", "priority")):
            bind_tags = kwargs.get("tags", ())
            bind_priority = kwargs.get("priority", 0)

            def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                if not hasattr(func, "_capability"):
                    desc = (func.__doc__ or "").strip().split("\n")[0].strip(".")
                    meta = CapabilityMetadata(
                        name=func.__name__,
                        capacity_type=CapabilityType.INFERENCE,
                        description=desc,
                        tags=tuple(bind_tags) if bind_tags else (),
                        priority=bind_priority,
                    )
                    func._capability = meta  # type: ignore[attr-defined]

                @functools.wraps(func)
                def wrapper(*call_args: Any, **call_kwargs: Any) -> Any:
                    meta = getattr(func, "_capability", None)
                    result = execute_inference(
                        func, meta, self, *call_args, **call_kwargs
                    )
                    if not result.success:
                        raise RuntimeError(
                            f"Inference failed for '{meta.name}': {result.error}"
                        ) from result.error
                    return result.value

                return wrapper

            return decorator

        # Direct execution: model.infer(func, *args, **kwargs)
        func = args[0]
        rest_args = args[1:]
        meta = getattr(func, "_capability", None)
        if meta is None:
            raise ValueError(
                f"Function '{func.__name__}' is not a registered capability. "
                f"Decorate it with @infer, @planner, or @router first."
            )

        result = execute_inference(func, meta, self, *rest_args, **kwargs)
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
