"""Roles and authorization context for OpenHosta V5 agents.

REQ-ROLE-001 — Role-based authorization context manager
DEF-ROLE-API-001 — Role API with principal, has_role and require_binding

This module provides a declarative, context-manager-based authorisation
mechanism for agent sessions:

1. **Principal** — opaque identity carrying a unique ID and a mutable
   set of role bindings.

2. **Roles** — context manager that establishes a scoped authority:
   ``with agent.roles()`` exposes ``self.principal``,
   ``self.has_role(name)`` and ``self.require_binding(name)``.

3. **RoleBindingError** — raised when a required role is absent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

# --------------------------------------------------------------------------- #
# RoleBindingError
# --------------------------------------------------------------------------- #


class RoleBindingError(Exception):
    """Raised when a required role binding is not satisfied.

    Parameters
    ----------
    role: str
        The missing role name.
    principal_id: str
        The principal that attempted the action.
    """

    def __init__(self, role: str, principal_id: str) -> None:
        super().__init__(
            f"Principal '{principal_id}' lacks required role '{role}'"
        )
        self.role = role
        self.principal_id = principal_id


# --------------------------------------------------------------------------- #
# Principal
# --------------------------------------------------------------------------- #


@dataclass
class Principal:
    """Represents an authenticated identity (agent, human, or system).

    Parameters
    ----------
    principal_id: str
        Globally unique identifier for this principal.
    name: str
        Human-readable name (may differ from principal_id).
    roles: set[str]
        Set of role identifiers currently bound to this principal.
    metadata: dict[str, str]
        Arbitrary key-value metadata attached to this principal.
    """

    principal_id: str
    name: str = ""
    roles: set[str] = field(default_factory=set)
    metadata: dict[str, str] = field(default_factory=dict)

    def grant(self, role: str) -> None:
        """Add *role* to this principal's bound roles."""
        self.roles.add(role)

    def revoke(self, role: str) -> None:
        """Remove *role* from this principal's bound roles.

        Does nothing (no-op) if the role is not currently bound.
        """
        self.roles.discard(role)

    def has_role(self, role: str) -> bool:
        """Return ``True`` if *role* is bound to this principal."""
        return role in self.roles

    def has_any(self, roles: Sequence[str]) -> bool:
        """Return ``True`` if *any* of the given roles are bound."""
        return bool(self.roles & set(roles))

    def has_all(self, roles: Sequence[str]) -> bool:
        """Return ``True`` if *all* of the given roles are bound."""
        return set(roles).issubset(self.roles)

    def effective_role_count(self) -> int:
        """Return the number of roles currently bound."""
        return len(self.roles)

    @property
    def display_name(self) -> str:
        """Human-readable ``name`` if set, otherwise ``principal_id``."""
        return self.name or self.principal_id


# --------------------------------------------------------------------------- #
# Roles — context manager providing scoped authorization
# --------------------------------------------------------------------------- #


class Roles:
    """Scoped role-authority context manager.

    Usage
    ~~~~~
    ::

        principal = Principal("agent-01", roles={"admin", "operator"})
        with Roles(principal) as r:
            assert r.principal.principal_id == "agent-01"
            assert r.has_role("admin")
            r.require_binding("operator")  # passes
            r.require_binding("auditor")   # raises RoleBindingError

    Parameters
    ----------
    principal: Principal
        The identity whose roles are scoped for this context.
    """

    def __init__(self, principal: Principal) -> None:
        self._principal = principal
        self._extra_roles: set[str] = set()

    def __enter__(self) -> Roles:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        _ = exc_type, exc_val, exc_tb
        # Cleanup extra in-context grants
        self._extra_roles.clear()

    @property
    def principal(self) -> Principal:
        """The principal whose roles are scoped for this context."""
        return self._principal

    @property
    def effective_roles(self) -> frozenset[str]:
        """Union of principal's permanent roles and in-context grants."""
        return frozenset(self._principal.roles | self._extra_roles)

    def has_role(self, role: str) -> bool:
        """Return ``True`` if *role* is effective within this scope."""
        return role in self._principal.roles or role in self._extra_roles

    def require_binding(self, role: str) -> None:
        """Assert that *role* is effective; raise ``RoleBindingError`` if absent.

        Parameters
        ----------
        role: str
            Required role name.

        Raises
        ------
        RoleBindingError
            When the principal (plus in-context grants) does not carry
            the required role.
        """
        if not self.has_role(role):
            raise RoleBindingError(role, self._principal.principal_id)

    def temporary_grant(self, role: str) -> None:
        """Grant *role* for the duration of this context only.

        The grant is automatically revoked on exit.
        """
        self._extra_roles.add(role)


# --------------------------------------------------------------------------- #
# Backward-compatible alias: ``agent.roles()`` returns a Roles instance
# --------------------------------------------------------------------------- #


def roles(principal: Principal) -> Roles:
    """Factory convenience: return a :class:`Roles` context manager.

    This is the canonical entry-point referenced in the spec::

        with agent.roles():
            assert agent.has_role("admin")
    """
    return Roles(principal)


# --------------------------------------------------------------------------- #
# Authority — helper to compose multi-principal checks
# --------------------------------------------------------------------------- #


@dataclass
class Authority:
    """Composite authority aggregating multiple principals.

    Parameters
    ----------
    principals: list[Principal]
        The principals contributing to this authority.
    """

    principals: list[Principal] = field(default_factory=list)

    def add(self, principal: Principal) -> Authority:
        """Add a principal and return self for chaining."""
        self.principals.append(principal)
        return self

    def has_role(self, role: str) -> bool:
        """Return ``True`` if **any** principal carries *role*."""
        return any(p.has_role(role) for p in self.principals)

    def require_all(self, role: str) -> None:
        """Raise ``RoleBindingError`` if **not all** principals carry *role*."""
        for p in self.principals:
            if not p.has_role(role):
                raise RoleBindingError(role, p.principal_id)
