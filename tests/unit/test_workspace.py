"""Tests for the governed Workspace filesystem abstraction."""

import os
import tempfile
from pathlib import Path

import pytest

from openhosta.workspace import Workspace


@pytest.fixture()
def tmp_workspace(tmp_path: Path) -> Workspace:
    ws = Workspace(tmp_path)
    return ws


class TestWorkspaceInit:
    def test_valid_root(self, tmp_path: Path) -> None:
        ws = Workspace(tmp_path)
        assert ws.root == tmp_path.resolve()

    def test_nonexistent_root(self) -> None:
        with pytest.raises(ValueError, match="does not exist"):
            Workspace("/nonexistent/absolute/path")

    def test_accepts_string_root(self, tmp_path: Path) -> None:
        ws = Workspace(str(tmp_path))
        assert ws.root == tmp_path.resolve()


class TestWorkspaceRead:
    def test_read_file(self, tmp_workspace: Workspace) -> None:
        tmp_workspace.write("hello.txt", "world")
        assert tmp_workspace.read("hello.txt") == "world"

    def test_read_nested_file(self, tmp_workspace: Workspace) -> None:
        tmp_workspace.write("sub/deep.txt", "nested content")
        assert tmp_workspace.read("sub/deep.txt") == "nested content"

    def test_read_nonexistent_raises(self, tmp_workspace: Workspace) -> None:
        with pytest.raises(FileNotFoundError):
            tmp_workspace.read("nope.txt")


class TestWorkspaceWrite:
    def test_write_creates_file(self, tmp_workspace: Workspace) -> None:
        tmp_workspace.write("new.txt", "content")
        assert (tmp_workspace.root / "new.txt").read_text() == "content"

    def test_write_overwrites(self, tmp_workspace: Workspace) -> None:
        tmp_workspace.write("new.txt", "v1")
        tmp_workspace.write("new.txt", "v2")
        assert tmp_workspace.read("new.txt") == "v2"

    def test_write_creates_parent_dirs(self, tmp_workspace: Workspace) -> None:
        tmp_workspace.write("a/b/c/nested.txt", "deep")
        assert tmp_workspace.read("a/b/c/nested.txt") == "deep"


class TestWorkspaceList:
    def test_list_root(self, tmp_workspace: Workspace) -> None:
        tmp_workspace.write("a.txt", "1")
        tmp_workspace.write("b.txt", "2")
        entries = tmp_workspace.list()
        assert "a.txt" in entries
        assert "b.txt" in entries

    def test_list_subdir(self, tmp_workspace: Workspace) -> None:
        tmp_workspace.write("sub/a.txt", "1")
        tmp_workspace.write("sub/b.txt", "2")
        entries = tmp_workspace.list("sub")
        assert entries == ["a.txt", "b.txt"]

    def test_list_empty(self, tmp_workspace: Workspace) -> None:
        assert tmp_workspace.list() == []

    def test_list_is_sorted(self, tmp_workspace: Workspace) -> None:
        tmp_workspace.write("c.txt", "")
        tmp_workspace.write("a.txt", "")
        tmp_workspace.write("b.txt", "")
        assert tmp_workspace.list() == ["a.txt", "b.txt", "c.txt"]


class TestWorkspaceExists:
    def test_exists_true(self, tmp_workspace: Workspace) -> None:
        tmp_workspace.write("yes.txt", "x")
        assert tmp_workspace.exists("yes.txt") is True

    def test_exists_false(self, tmp_workspace: Workspace) -> None:
        assert tmp_workspace.exists("no.txt") is False

    def test_exists_escaping_returns_false(self, tmp_workspace: Workspace) -> None:
        assert tmp_workspace.exists("../../etc/passwd") is False


class TestWorkspaceStat:
    def test_stat_file(self, tmp_workspace: Workspace) -> None:
        tmp_workspace.write("s.txt", "abc")
        info = tmp_workspace.stat("s.txt")
        assert info["size"] == 3
        assert info["is_file"] is True
        assert info["is_dir"] is False
        assert "modified" in info

    def test_stat_dir(self, tmp_workspace: Workspace) -> None:
        tmp_workspace.write("d/f.txt", "x")
        info = tmp_workspace.stat("d")
        assert info["is_dir"] is True
        assert info["is_file"] is False


class TestWorkspacePatch:
    def test_patch_writes_content(self, tmp_workspace: Workspace) -> None:
        tmp_workspace.patch("p.txt", "patched")
        assert tmp_workspace.read("p.txt") == "patched"


class TestWorkspaceSecurity:
    def test_read_escapes_raises(self, tmp_workspace: Workspace) -> None:
        with pytest.raises(PermissionError, match="escapes workspace"):
            tmp_workspace.read("../../etc/passwd")

    def test_write_escapes_raises(self, tmp_workspace: Workspace) -> None:
        with pytest.raises(PermissionError, match="escapes workspace"):
            tmp_workspace.write("../../tmp/evil.txt", "hack")

    def test_list_escapes_raises(self, tmp_workspace: Workspace) -> None:
        with pytest.raises(PermissionError, match="escapes workspace"):
            tmp_workspace.list("..")

    def test_stat_escapes_raises(self, tmp_workspace: Workspace) -> None:
        with pytest.raises(PermissionError, match="escapes workspace"):
            tmp_workspace.stat("../secret")

    def test_cannot_reach_parent_through_symlink(
        self, tmp_path: Path
    ) -> None:
        outside_file = tmp_path / ".." / "outside_test_file.txt"
        outside_file.write_text("secret")

        ws_dir = tmp_path / "workspace"
        ws_dir.mkdir()
        ws = Workspace(ws_dir)

        link_dir = ws_dir / "link_dir"
        link_dir.mkdir()
        (link_dir / "escape").symlink_to(tmp_path / "..")

        with pytest.raises(PermissionError, match="escapes workspace"):
            ws.read("link_dir/escape/outside_test_file.txt")

        outside_file.unlink()
