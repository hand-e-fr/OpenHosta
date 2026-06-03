# Workspace — OpenHosta V5

## Overview

`Workspace` provides governed, security-aware access to the project filesystem.
All paths are resolved relative to a workspace root to prevent directory
traversal attacks.

## Construction

```python
from openhosta import Workspace
from pathlib import Path

ws = Workspace("/path/to/project")  # str or Path
```

If the path does not exist or is not a directory, `ValueError` is raised.
The root is resolved to an absolute path on construction.

## API

### `ws.read(path: str) -> str`

Read a file as UTF-8 text. The path is resolved relative to the workspace root.

```python
content = ws.read("src/main.py")
```

### `ws.list(path: str | None = None) -> list[str]`

List directory entries (sorted by name). `None` lists the root.

```python
entries = ws.list("src")      # entries in src/
entries = ws.list()           # entries in workspace root
```

### `ws.exists(path: str) -> bool`

Check if a path exists. Returns `False` for paths that escape the workspace.

```python
if ws.exists("README.md"):
    ...
```

### `ws.stat(path: str) -> dict[str, Any]`

Return metadata about a path:

```python
info = ws.stat("src/main.py")
# {"size": 1234, "is_file": True, "is_dir": False, "modified": 1717300000.0}
```

### `ws.write(path: str, content: str) -> None`

Write content to a file. Creates intermediate directories automatically.

```python
ws.write("output/report.txt", "Generated report content")
```

### `ws.patch(path: str, content: str) -> None`

Append or update file content. Currently behaves identically to `write` but
preserves the semantic intent of a revision operation.

## Security

The `_safe(path)` method enforces confinement:

```python
def _safe(self, path: str) -> Path:
    target = (self.root / path).resolve()
    if not str(target).startswith(str(self.root)):
        raise PermissionError(
            f"Path escapes workspace root: {path} -> {target}"
        )
    return target
```

Any path that resolves outside the workspace root raises `PermissionError`.

### Escaping Examples

These all raise `PermissionError`:

```python
ws.read("../secrets")       # .. traversal
ws.read("/etc/passwd")      # absolute path
ws.read("src/../../../etc") # deep traversal
```

## Agent Integration

Every `Agent` has a `workspace` property:

```python
from openhosta import Agent, Workspace

agent = Agent(workspace=Workspace("/tmp/my-workspace"))
content = agent.workspace.read("my_file.txt")
```

If no workspace is provided, a default `Workspace(Path("."))` is created:

```python
agent = Agent()  # workspace = current directory
```
