# mypy: ignore-errors
"""Public declarative API for guarded types: guard() / unguard()."""

from typing import Any

from .primitives import GuardedPrimitive
from .resolver import TypeResolver
from .wrapper import Guarded, GuardMetadata
from .wrapper import guard as wrapper_guard
from .wrapper import unguard as wrapper_unguard


def guard[T](value: T, target: type | None = None) -> Any:
    """Wrap a value in a Guarded type with runtime validation.

    Accepts either a type annotation or GuardMetadata as the second argument.

    Args:
        value: The value to guard.
        target: Optional target type annotation or GuardMetadata instance.
                When a type is provided, it resolves via TypeResolver.
                When GuardMetadata is provided, delegates to the wrapper guard().
                When omitted, delegates to the wrapper guard() for proxy wrapping.

    Returns:
        A Guarded instance carrying the casted value and metadata.

    Raises:
        ValueError: When the pipeline cannot cast *value* to *target*.
    """
    if isinstance(value, Guarded):
        return value

    if isinstance(target, GuardMetadata):
        return wrapper_guard(value, target)

    if target is None:
        return wrapper_guard(value)

    guarded_type = TypeResolver.resolve(target)
    return guarded_type(value)


def unguard(value: GuardedPrimitive) -> object:
    """Extract the native value from a Guarded wrapper.

    Handles both GuardedPrimitive instances and Guarded[T] proxy wrappers.
    Recursively unwraps containers (list, dict, tuple, dataclass).

    Args:
        value: A Guarded instance or native value.

    Returns:
        The unwrapped Python value.

    Raises:
        ValueError: When the Guarded instance represents a failed cast.
    """
    if isinstance(value, Guarded):
        return wrapper_unguard(value)

    if isinstance(value, GuardedPrimitive):
        if value.abstraction_level == "failed":
            raise ValueError(
                f"Cannot unguard failed Guarded instance. "
                f"Original error: {getattr(value, '_input', '<unknown>')}"
            )
        return value.unwrap()

    # For non-Guarded values, delegate to wrapper.unguard to handle
    # recursive unwrapping of containers (list, dict, tuple, dataclass)
    return wrapper_unguard(value)
