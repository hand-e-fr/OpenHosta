"""Internal configuration for agent module.

This module provides runtime configuration for the agent system,
particularly backend resolution for inference capabilities.
"""

from __future__ import annotations

from typing import Any

from openhosta.backend import BackendModel


# Global default backend (None = not configured)
_default_backend: BackendModel | None = None


def set_default_backend(backend: BackendModel | None) -> None:
    """Set the global default backend for inference capabilities.

    Parameters
    ----------
    backend: BackendModel | None
        The backend to use by default, or None to clear.
    """
    global _default_backend
    _default_backend = backend


def get_default_backend() -> BackendModel | None:
    """Return the current default backend, or None if not configured."""
    return _default_backend
