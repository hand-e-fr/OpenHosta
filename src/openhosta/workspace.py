from __future__ import annotations

import os
import stat as stat_module
from pathlib import Path
from typing import Any


class Workspace:
    """Governed access surface to the project filesystem.

    All paths are resolved relative to the workspace root to prevent
    access outside the project directory.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise ValueError(f"Workspace root does not exist: {self.root}")

    def _safe(self, path: str) -> Path:
        """Resolve *path* relative to the workspace root and enforce confinement."""
        target = (self.root / path).resolve()
        if not str(target).startswith(str(self.root)):
            raise PermissionError(
                f"Path escapes workspace root: {path} -> {target}"
            )
        return target

    def read(self, path: str) -> str:
        target = self._safe(path)
        return target.read_text(encoding="utf-8")

    def list(self, path: str | None = None) -> list[str]:
        target = self._safe(path) if path is not None else self.root
        return sorted(entry.name for entry in target.iterdir())

    def exists(self, path: str) -> bool:
        try:
            target = self._safe(path)
        except PermissionError:
            return False
        return target.exists()

    def stat(self, path: str) -> dict[str, Any]:
        target = self._safe(path)
        st = target.stat()
        return {
            "size": st.st_size,
            "is_file": stat_module.S_ISREG(st.st_mode),
            "is_dir": stat_module.S_ISDIR(st.st_mode),
            "modified": st.st_mtime,
        }

    def write(self, path: str, content: str) -> None:
        target = self._safe(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def patch(self, path: str, content: str) -> None:
        """Append or update file content.

        Currently behaves identically to write but preserves the
        semantic intent of a revision operation.
        """
        self.write(path, content)
