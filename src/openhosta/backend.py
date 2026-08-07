from __future__ import annotations

import functools
import inspect as _inspect
import json
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING
from collections.abc import Callable

from openhosta.agent.capability import (
    CapabilityMetadata,
    CapabilityRegistration,
    CapabilityType,
)
from openhosta.agent.inference import execute_inference, is_stub

if TYPE_CHECKING:
    pass


@dataclass
class BackendModel:
    """Describes a single LLM backend configuration.

    Every decorator (``@model.infer()``, ``@model.tool()``, etc.) registers
    the decorated function in ``self._capabilities`` so that the model
    instance can introspect its own capabilities at runtime.
    """

    provider: str
    model_name: str
    base_url: str
    api_key: str = ""
    tags: tuple[str, ...] = ()
    priority: int = 0
    headers: dict[str, str] = field(default_factory=dict)
    body: dict[str, Any] = field(default_factory=dict)
    model_params: dict[str, Any] = field(default_factory=dict)
    timeout: int = 120
    return_type_schema: str = "python"
    _capabilities: CapabilityRegistration = field(
        default_factory=CapabilityRegistration, repr=False
    )

    # ------------------------------------------------------------------ #
    # Introspection API
    # ------------------------------------------------------------------ #

    @property
    def capabilities(
        self,
    ) -> list[tuple[Callable[..., Any], CapabilityMetadata]]:
        """Return every registered capability on this model instance."""
        return self._capabilities.list_all()

    @property
    def cap_count(self) -> int:
        """Number of registered capabilities."""
        return self._capabilities.count

    def get_capability(self, name: str) -> CapabilityMetadata:
        """Return the ``CapabilityMetadata`` for *name*, or raise ``KeyError``."""
        _, meta = self._capabilities.get(name)
        return meta

    def find_capability(self, name: str) -> CapabilityMetadata | None:
        """Return the ``CapabilityMetadata`` for *name*, or ``None``."""
        entry = self._capabilities.find_by_name(name)
        return entry[1] if entry else None

    def find_by_tag(self, tag: str) -> list[CapabilityMetadata]:
        """Return all capability metadata tagged with *tag*."""
        return [meta for _, meta in self._capabilities.find_by_tag(tag)]

    def find_by_type(
        self, capacity_type: CapabilityType
    ) -> list[CapabilityMetadata]:
        """Return all capability metadata matching *capacity_type*."""
        return [meta for _, meta in self._capabilities.find_by_type(capacity_type)]

    def to_dict(self) -> dict[str, Any]:
        """Serialize capabilities to a plain dict (JSON-friendly)."""
        return {
            "provider": self.provider,
            "model_name": self.model_name,
            "base_url": self.base_url,
            "tags": list(self.tags),
            "priority": self.priority,
            "capabilities": [
                {
                    "name": meta.name,
                    "type": meta.capacity_type.name,
                    "description": meta.description,
                    "tags": list(meta.tags),
                    "priority": meta.priority,
                }
                for _, meta in self._capabilities.list_all()
            ],
        }

    def dispatch(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a registered capability by name.

        Shorthand for looking up the callable via ``get_capability``
        and invoking it with this backend injected.
        """
        func, meta = self._capabilities.get(name)
        result = execute_inference(func, meta, self, *args, **kwargs)
        if not result.success:
            raise RuntimeError(
                f"Inference failed for '{meta.name}': {result.error}"
            ) from result.error
        return result.value

    # ------------------------------------------------------------------ #
    # Utility: build CapabilityMetadata from func
    # ------------------------------------------------------------------ #

    def _build_metadata(
        self,
        func: Callable[..., Any],
        capacity_type: CapabilityType,
        name: str | None = None,
        description: str | None = None,
        tags: tuple[str, ...] = (),
        priority: int = 0,
        requires_async: bool = False,
    ) -> CapabilityMetadata:
        """Build CapabilityMetadata from *func*, mirroring capability.py logic."""
        resolved_name = name if name is not None else func.__name__

        docstring = (func.__doc__ or "").strip()
        first_line = ""
        for line in docstring.splitlines():
            stripped = line.strip()
            if stripped:
                first_line = stripped
                break
        resolved_desc = (
            description if description is not None else first_line
        )

        # Build long_description
        sig_summary = ""
        try:
            sig = _inspect.signature(func)
            sig_summary = f"{func.__name__}{sig}"
        except (ValueError, TypeError):
            sig_summary = func.__name__

        long_desc_parts = [f"**Signature:** `{sig_summary}`"]
        if docstring:
            long_desc_parts.append(f"\n**Docstring:**\n{docstring}")
        long_desc = "\n".join(long_desc_parts)

        return CapabilityMetadata(
            name=resolved_name,
            capacity_type=capacity_type,
            description=resolved_desc,
            long_description=long_desc,
            tags=tags,
            priority=priority,
            requires_async=requires_async,
        )

    # ------------------------------------------------------------------ #
    # Utility: wrap a potentially-stub function with inference delegation
    # ------------------------------------------------------------------ #

    def _wrap_infer(
        self,
        func: Callable[..., Any],
        meta: CapabilityMetadata,
        bind_headers: dict[str, str] | None = None,
        bind_body: dict[str, Any] | None = None,
        bind_model_params: dict[str, Any] | None = None,
        bind_timeout: int = 120,
        bind_schema_style: str = "python",
    ) -> Callable[..., Any]:
        """If *func* is a stub, wrap it to delegate to InferenceEngine."""
        if not is_stub(func):
            return func

        @functools.wraps(func)
        def _infer_wrapper(*call_args: Any, **call_kwargs: Any) -> Any:
            if bind_headers:
                call_kwargs.setdefault("__infer_headers__", bind_headers)
            if bind_body:
                call_kwargs.setdefault("__infer_body__", bind_body)
            if bind_model_params:
                call_kwargs.setdefault("__infer_model_params__", bind_model_params)
            if bind_timeout != 120:
                call_kwargs.setdefault("__infer_timeout__", bind_timeout)
            call_kwargs.setdefault("__infer_schema_style__", bind_schema_style)
            result = execute_inference(
                func, meta, self, *call_args, **call_kwargs
            )
            if not result.success:
                raise RuntimeError(
                    f"Inference failed for '{meta.name}': {result.error}"
                ) from result.error
            return result.value

        return _infer_wrapper

    # ------------------------------------------------------------------ #
    # Decorators
    # ------------------------------------------------------------------ #

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
            Always -- ``BackendModel`` instances must not be called directly.
        """
        if not args and any(k in kwargs for k in ("tags", "priority")):
            raise TypeError(
                "BackendModel is not a decorator. "
                "Use ``@model.infer(tags=[...])`` as the decorator, "
                "not ``@model(tags=[...])``. "
                "See: model.infer(func, ...) for standalone inference."
            )

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
    # infer: decorator always requires parens @model.infer()
    # ------------------------------------------------------------------ #

    def infer(
        self,
        name: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        priority: int = 0,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        model_params: dict[str, Any] | None = None,
        timeout: int = 120,
        return_type_schema: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator: mark a function as a backend inference capability.

        Always use with parentheses: ``@model.infer()`` or ``@model.infer(tags=[...])``.

        Parameters
        ----------
        name: str | None
            Custom capability name. Defaults to ``func.__name__``.
        description: str | None
            Override short description. Defaults to first docstring line.
        tags: list[str] | None
            Capability tags for routing and filtering.
        priority: int
            Scheduling priority (lower = more urgent). Default ``0``.
        headers: dict[str, str] | None
            Extra HTTP headers sent with every inference request.
        body: dict[str, Any] | None
            Extra JSON body fields merged into the API request.
        model_params: dict[str, Any] | None
            Model parameters (temperature, max_tokens, etc.) merged into request.
        timeout: int
            Request timeout in seconds.
        return_type_schema: str | None
            Format for custom type schema in the prompt. ``"json"`` (default)
            produces JSON Schema. ``"python"`` produces Python dataclass/enum
            source code. ``None`` inherits from ``self.return_type_schema``.

        Examples
        --------
            @model.infer()
            def translate(text: str) -> str: ...

            @model.infer(return_type_schema="python")
            def translate(text: str) -> str: ...

            @model.infer(name="fr_to_en", tags=["lang"])
            def translate(text: str) -> str: ...
        """
        # Catch misuse: @model.infer (missing parens) → first positional is callable
        # When called as @model.infer, Python passes func as `name`
        if name is not None and callable(name):
            func_name = getattr(name, "__name__", repr(name))
            raise TypeError(
                f"Missing parentheses on decorator. "
                f"Use ``@model.infer()`` not ``@model.infer``.\n"
                f"    @model.infer()\n"
                f"    def {func_name}(...): ..."
            )

        bind_tags = tuple(tags) if tags else ()
        bind_headers = dict(headers) if headers else {}
        bind_body = dict(body) if body else {}
        bind_model_params = dict(model_params) if model_params else {}
        bind_timeout = timeout
        bind_schema_style = return_type_schema if return_type_schema is not None else self.return_type_schema

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            if not hasattr(func, "_capability"):
                meta = self._build_metadata(
                    func,
                    CapabilityType.INFERENCE,
                    name=name,
                    description=description,
                    tags=bind_tags,
                    priority=priority,
                )
                func._capability = meta  # type: ignore[attr-defined]
            else:
                meta = getattr(func, "_capability")

            wrapped = self._wrap_infer(
                func, meta,
                bind_headers=bind_headers or None,
                bind_body=bind_body or None,
                bind_model_params=bind_model_params or None,
                bind_timeout=bind_timeout,
                bind_schema_style=bind_schema_style,
            )

            self._capabilities.register(wrapped, meta)
            return wrapped

        return decorator

    # ------------------------------------------------------------------ #
    # tool: decorator always requires parens @model.tool()
    # ------------------------------------------------------------------ #

    def tool(
        self,
        name: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        priority: int = 0,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator: mark a function as a **tool** capability (deterministic routine).

        Example
        -------
            @model.tool(tags=["files"])
            def read_file(path: str) -> str:
                \"\"\"Read the file at *path\"\"\"
                return Path(path).read_text()
        """
        if name is not None and callable(name):
            func_name = getattr(name, "__name__", repr(name))
            raise TypeError(
                f"Missing parentheses on decorator. "
                f"Use ``@model.tool()`` not ``@model.tool``.\n"
                f"    @model.tool()\n"
                f"    def {func_name}(...): ..."
            )

        bind_tags = tuple(tags) if tags else ()

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            meta = self._build_metadata(
                func,
                CapabilityType.TOOL,
                name=name,
                description=description,
                tags=bind_tags,
                priority=priority,
            )
            func._capability = meta  # type: ignore[attr-defined]
            self._capabilities.register(func, meta)
            return func

        return decorator

    # ------------------------------------------------------------------ #
    # planner: decorator @model.planner()
    # ------------------------------------------------------------------ #

    def planner(
        self,
        name: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        priority: int = 0,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        model_params: dict[str, Any] | None = None,
        timeout: int = 120,
        return_type_schema: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator: mark a function as a **planner** capability (goal decomposition)."""
        if name is not None and callable(name):
            func_name = getattr(name, "__name__", repr(name))
            raise TypeError(
                f"Missing parentheses on decorator. "
                f"Use ``@model.planner()`` not ``@model.planner``.\n"
                f"    @model.planner()\n"
                f"    def {func_name}(...): ..."
            )

        bind_tags = tuple(tags) if tags else ()
        bind_headers = dict(headers) if headers else {}
        bind_body = dict(body) if body else {}
        bind_model_params = dict(model_params) if model_params else {}
        bind_timeout = timeout
        bind_schema_style = return_type_schema if return_type_schema is not None else self.return_type_schema

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            meta = self._build_metadata(
                func,
                CapabilityType.PLANNER,
                name=name,
                description=description,
                tags=bind_tags,
                priority=priority,
            )
            func._capability = meta  # type: ignore[attr-defined]

            wrapped = self._wrap_infer(
                func, meta,
                bind_headers=bind_headers or None,
                bind_body=bind_body or None,
                bind_model_params=bind_model_params or None,
                bind_timeout=bind_timeout,
                bind_schema_style=bind_schema_style,
            )

            self._capabilities.register(wrapped, meta)
            return wrapped

        return decorator

    # ------------------------------------------------------------------ #
    # router: decorator @model.router()
    # ------------------------------------------------------------------ #

    def router(
        self,
        name: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        priority: int = 0,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        model_params: dict[str, Any] | None = None,
        timeout: int = 120,
        return_type_schema: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator: mark a function as a **router** capability (routing decision)."""
        if name is not None and callable(name):
            func_name = getattr(name, "__name__", repr(name))
            raise TypeError(
                f"Missing parentheses on decorator. "
                f"Use ``@model.router()`` not ``@model.router``.\n"
                f"    @model.router()\n"
                f"    def {func_name}(...): ..."
            )

        bind_tags = tuple(tags) if tags else ()
        bind_headers = dict(headers) if headers else {}
        bind_body = dict(body) if body else {}
        bind_model_params = dict(model_params) if model_params else {}
        bind_timeout = timeout
        bind_schema_style = return_type_schema if return_type_schema is not None else self.return_type_schema

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            meta = self._build_metadata(
                func,
                CapabilityType.ROUTER,
                name=name,
                description=description,
                tags=bind_tags,
                priority=priority,
            )
            func._capability = meta  # type: ignore[attr-defined]

            wrapped = self._wrap_infer(
                func, meta,
                bind_headers=bind_headers or None,
                bind_body=bind_body or None,
                bind_model_params=bind_model_params or None,
                bind_timeout=bind_timeout,
                bind_schema_style=bind_schema_style,
            )

            self._capabilities.register(wrapped, meta)
            return wrapped

        return decorator

    # ------------------------------------------------------------------ #
    # playbook: decorator @model.playbook()
    # ------------------------------------------------------------------ #

    def playbook(
        self,
        name: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        priority: int = 0,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator: mark a function as a **playbook** capability (multi-step workflow)."""
        if name is not None and callable(name):
            func_name = getattr(name, "__name__", repr(name))
            raise TypeError(
                f"Missing parentheses on decorator. "
                f"Use ``@model.playbook()`` not ``@model.playbook``.\n"
                f"    @model.playbook()\n"
                f"    def {func_name}(...): ..."
            )

        bind_tags = tuple(tags) if tags else ()

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            meta = self._build_metadata(
                func,
                CapabilityType.PLAYBOOK,
                name=name,
                description=description,
                tags=bind_tags,
                priority=priority,
            )
            func._capability = meta  # type: ignore[attr-defined]
            self._capabilities.register(func, meta)
            return func

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
