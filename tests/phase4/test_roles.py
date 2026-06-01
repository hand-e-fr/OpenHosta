"""Tests for roles module — Principal, Roles, RoleBindingError, Authority, roles().

REQ-ROLE-001 — Role-based authorization context manager
DEF-ROLE-API-001 — Role API with principal, has_role and require_binding
"""

from __future__ import annotations

import pytest

from next_v5.agent.roles import Authority, Principal, RoleBindingError, Roles, roles

# ============================================================================
# TestPrincipal
# ============================================================================


class TestPrincipal:
    def test_default_values(self) -> None:
        p = Principal(principal_id="p1")
        assert p.principal_id == "p1"
        assert p.name == ""
        assert p.roles == set()
        assert p.metadata == {}

    def test_display_name_falls_back_to_principal_id(self) -> None:
        p = Principal(principal_id="p1")
        assert p.display_name == "p1"

    def test_display_name_uses_name_when_set(self) -> None:
        p = Principal(principal_id="p1", name="Alice")
        assert p.display_name == "Alice"

    def test_grant_adds_role(self) -> None:
        p = Principal(principal_id="p1")
        p.grant("admin")
        assert "admin" in p.roles

    def test_revoke_removes_role(self) -> None:
        p = Principal(principal_id="p1", roles={"admin"})
        p.revoke("admin")
        assert "admin" not in p.roles

    def test_revoke_noop_when_absent(self) -> None:
        p = Principal(principal_id="p1")
        p.revoke("admin")
        assert "admin" not in p.roles

    def test_has_role_true(self) -> None:
        p = Principal(principal_id="p1", roles={"admin"})
        assert p.has_role("admin") is True

    def test_has_role_false(self) -> None:
        p = Principal(principal_id="p1", roles={"admin"})
        assert p.has_role("operator") is False

    def test_has_any_true(self) -> None:
        p = Principal(principal_id="p1", roles={"admin"})
        assert p.has_any(["operator", "admin"]) is True

    def test_has_any_false(self) -> None:
        p = Principal(principal_id="p1", roles={"admin"})
        assert p.has_any(["operator", "auditor"]) is False

    def test_has_all_true(self) -> None:
        p = Principal(principal_id="p1", roles={"admin", "operator"})
        assert p.has_all(["admin", "operator"]) is True

    def test_has_all_false(self) -> None:
        p = Principal(principal_id="p1", roles={"admin"})
        assert p.has_all(["admin", "operator"]) is False

    def test_effective_role_count(self) -> None:
        p = Principal(principal_id="p1", roles={"admin", "operator", "auditor"})
        assert p.effective_role_count() == 3

    def test_effective_role_count_empty(self) -> None:
        p = Principal(principal_id="p1")
        assert p.effective_role_count() == 0


# ============================================================================
# TestRolesContextManager
# ============================================================================


class TestRolesContextManager:
    def test_enter_returns_self(self) -> None:
        p = Principal(principal_id="p1")
        r = Roles(p)
        assert r.__enter__() is r

    def test_exit_clears_extra_roles(self) -> None:
        p = Principal(principal_id="p1")
        r = Roles(p)
        r.temporary_grant("temp_role")
        r.__exit__(None, None, None)
        assert r.has_role("temp_role") is False

    def test_has_role_checks_principal(self) -> None:
        p = Principal(principal_id="p1", roles={"admin"})
        r = Roles(p)
        assert r.has_role("admin") is True
        assert r.has_role("operator") is False

    def test_require_binding_passes_when_role_present(self) -> None:
        p = Principal(principal_id="p1", roles={"admin"})
        r = Roles(p)
        r.require_binding("admin")

    def test_require_binding_raises_when_absent(self) -> None:
        p = Principal(principal_id="p1", roles={"admin"})
        r = Roles(p)
        with pytest.raises(RoleBindingError) as exc_info:
            r.require_binding("operator")
        assert exc_info.value.role == "operator"
        assert exc_info.value.principal_id == "p1"

    def test_temporary_grant_adds_role_inside_context(self) -> None:
        p = Principal(principal_id="p1", roles={"admin"})
        r = Roles(p)
        r.temporary_grant("operator")
        assert r.has_role("operator") is True
        assert "operator" not in p.roles  # original principal unchanged

    def test_temporary_grant_removed_after_exit(self) -> None:
        p = Principal(principal_id="p1")
        r = Roles(p)
        with r:
            r.temporary_grant("temp")
            assert r.has_role("temp") is True
        assert r.has_role("temp") is False

    def test_effective_roles_property(self) -> None:
        p = Principal(principal_id="p1", roles={"admin"})
        r = Roles(p)
        r.temporary_grant("operator")
        assert r.effective_roles == frozenset({"admin", "operator"})


# ============================================================================
# TestRolesFactory
# ============================================================================


class TestRolesFactory:
    def test_roles_returns_roles_instance(self) -> None:
        p = Principal(principal_id="p1")
        r = roles(p)
        assert isinstance(r, Roles)
        assert r.principal.principal_id == "p1"


# ============================================================================
# TestRoleBindingError
# ============================================================================


class TestRoleBindingError:
    def test_error_message_includes_role_and_principal_id(self) -> None:
        err = RoleBindingError(role="admin", principal_id="p1")
        assert "admin" in str(err)
        assert "p1" in str(err)

    def test_attributes_are_set(self) -> None:
        err = RoleBindingError(role="operator", principal_id="agent-42")
        assert err.role == "operator"
        assert err.principal_id == "agent-42"


# ============================================================================
# TestAuthority
# ============================================================================


class TestAuthority:
    def test_has_role_checks_any_principal(self) -> None:
        p1 = Principal(principal_id="p1", roles={"admin"})
        p2 = Principal(principal_id="p2", roles={"operator"})
        auth = Authority(principals=[p1, p2])
        assert auth.has_role("admin") is True
        assert auth.has_role("operator") is True
        assert auth.has_role("auditor") is False

    def test_has_role_empty_authority(self) -> None:
        auth = Authority()
        assert auth.has_role("admin") is False

    def test_require_all_passes_when_all_have_role(self) -> None:
        p1 = Principal(principal_id="p1", roles={"admin"})
        p2 = Principal(principal_id="p2", roles={"admin", "operator"})
        auth = Authority(principals=[p1, p2])
        auth.require_all("admin")

    def test_require_all_raises_when_one_lacks_role(self) -> None:
        p1 = Principal(principal_id="p1", roles={"admin"})
        p2 = Principal(principal_id="p2", roles={"operator"})
        auth = Authority(principals=[p1, p2])
        with pytest.raises(RoleBindingError) as exc_info:
            auth.require_all("admin")
        assert exc_info.value.role == "admin"
        assert exc_info.value.principal_id == "p2"

    def test_add_returns_self_for_chaining(self) -> None:
        auth = Authority()
        ret = auth.add(Principal(principal_id="p1"))
        assert ret is auth
        assert len(auth.principals) == 1
