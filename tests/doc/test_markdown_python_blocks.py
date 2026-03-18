import ast
import re
import textwrap
from pathlib import Path

import pytest
from dotenv import load_dotenv


load_dotenv()


DOCS_ROOT = Path(__file__).resolve().parents[2] / "docs"
PYTHON_BLOCK_RE = re.compile(r"```python[^\n]*\n(.*?)\n```", re.DOTALL)

SAFE_ONLY_DOCS = {
    "safe_context_and_uncertainty.md",
}

GENERATE_ONLY_DOCS = {
    # Add docs here if/when markdown examples explicitly use generate().
}

COMMON_GLOBALS = {
    "__name__": "__doc_test__",
}

DOC_TEST_RAISES_RE = re.compile(r"^\s*#\s*doc-test:\s*raises\s+([A-Za-z_][A-Za-z0-9_\.]*)\s*$", re.MULTILINE)
NETWORK_EXCEPTIONS = ("RequestError", "SSLError", "ConnectionError", "ConnectTimeout", "ReadTimeout")


def _iter_python_blocks():
    for md_path in sorted(DOCS_ROOT.rglob("*.md")):
        content = md_path.read_text(encoding="utf-8")
        for index, match in enumerate(PYTHON_BLOCK_RE.finditer(content), start=1):
            code = textwrap.dedent(match.group(1)).strip()
            yield md_path, index, code


def _compile_block(md_path: Path, block_index: int, code: str):
    try:
        return compile(code, f"{md_path.as_posix()}::python-block-{block_index}", "exec")
    except SyntaxError as exc:
        pytest.fail(
            f"Syntax error in markdown python block {block_index} from {md_path.relative_to(DOCS_ROOT)}: {exc}"
        )


def _parse_tree(code: str):
    try:
        return ast.parse(code)
    except SyntaxError:
        return None


def _uses_name(code: str, target_name: str) -> bool:
    tree = _parse_tree(code)
    if tree is None:
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == target_name:
                return True
    return False


def _imports_module(code: str, module_name: str) -> bool:
    tree = _parse_tree(code)
    if tree is None:
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == module_name or alias.name.startswith(module_name + "."):
                    return True
        elif isinstance(node, ast.ImportFrom):
            if node.module == module_name or (node.module and node.module.startswith(module_name + ".")):
                return True
    return False


def _get_expected_exception_name(code: str):
    match = DOC_TEST_RAISES_RE.search(code)
    if match:
        return match.group(1)
    return None


def _resolve_exception_type(expected_name: str, namespace: dict):
    if "." not in expected_name:
        exc_type = namespace.get(expected_name)
        if isinstance(exc_type, type) and issubclass(exc_type, BaseException):
            return exc_type
        import builtins
        exc_type = getattr(builtins, expected_name, None)
        if isinstance(exc_type, type) and issubclass(exc_type, BaseException):
            return exc_type
        return None

    current = namespace.get(expected_name.split(".")[0])
    if current is None:
        import builtins
        current = getattr(builtins, expected_name.split(".")[0], None)
    for part in expected_name.split(".")[1:]:
        current = getattr(current, part, None)
        if current is None:
            return None
    if isinstance(current, type) and issubclass(current, BaseException):
        return current
    return None


def _doc_kind(md_path: Path, code: str) -> str:
    relative = md_path.relative_to(DOCS_ROOT).as_posix()

    if relative in {f"examples/{name}" for name in GENERATE_ONLY_DOCS} or md_path.name in GENERATE_ONLY_DOCS:
        return "generate"

    if relative in {f"{name}" for name in SAFE_ONLY_DOCS} or md_path.name in SAFE_ONLY_DOCS:
        return "safe"

    if _uses_name(code, "safe"):
        return "safe"

    if _uses_name(code, "generate"):
        return "generate"

    if any(_uses_name(code, name) for name in ("ask", "ask_async", "emulate", "emulate_async", "closure")):
        return "generate"

    if _imports_module(code, "OpenHosta.asynchrone"):
        return "generate"

    return "general"


GENERAL_BLOCKS = []
SAFE_BLOCKS = []
GENERATE_BLOCKS = []

for _md_path, _block_index, _code in _iter_python_blocks():
    _kind = _doc_kind(_md_path, _code)
    _entry = pytest.param(_md_path, _block_index, _code, id=f"{_md_path.relative_to(DOCS_ROOT).as_posix()}::block{_block_index}")
    if _kind == "safe":
        SAFE_BLOCKS.append(_entry)
    elif _kind == "generate":
        GENERATE_BLOCKS.append(_entry)
    else:
        GENERAL_BLOCKS.append(_entry)


def _execute_block(md_path: Path, block_index: int, code: str):
    compiled = _compile_block(md_path, block_index, code)
    namespace = dict(COMMON_GLOBALS)
    expected_exception_name = _get_expected_exception_name(code)

    if expected_exception_name:
        expected_exception_type = _resolve_exception_type(expected_exception_name, namespace)
        if expected_exception_type is None:
            pytest.fail(
                f"Could not resolve expected exception '{expected_exception_name}' for "
                f"{md_path.relative_to(DOCS_ROOT)} block {block_index}."
            )
        with pytest.raises(expected_exception_type):
            exec(compiled, namespace, namespace)
        return

    try:
        exec(compiled, namespace, namespace)
    except Exception as exc:
        if exc.__class__.__name__ in NETWORK_EXCEPTIONS:
            pytest.skip(
                f"Skipped network/proxy-dependent failure in {md_path.relative_to(DOCS_ROOT)} "
                f"block {block_index}: {exc}"
            )
        if exc.__class__.__name__ == "RequestError":
            pytest.skip(
                f"Skipped request/proxy-dependent failure in {md_path.relative_to(DOCS_ROOT)} "
                f"block {block_index}: {exc}"
            )
        raise


@pytest.mark.parametrize(("md_path", "block_index", "code"), GENERAL_BLOCKS)
def test_general_markdown_python_blocks(md_path: Path, block_index: int, code: str):
    _execute_block(md_path, block_index, code)


@pytest.mark.parametrize(("md_path", "block_index", "code"), SAFE_BLOCKS)
def test_safe_markdown_python_blocks(md_path: Path, block_index: int, code: str):
    _execute_block(md_path, block_index, code)


@pytest.mark.parametrize(("md_path", "block_index", "code"), GENERATE_BLOCKS)
def test_generate_markdown_python_blocks(md_path: Path, block_index: int, code: str):
    _execute_block(md_path, block_index, code)