"""Inference Engine — bridge between decorated capabilities and the LLM backend.

This module is the core delegation mechanism:
1. Extract signature + docstring from a decorated function
2. Build a structured prompt
3. Call the backend via OpenAI-compatible API
4. Parse the response using guarded types
5. Return Guarded[T] with GuardMetadata
"""

from __future__ import annotations

import ast
import inspect
import json
import textwrap
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Any

from openhosta.guarded.api import guard
from openhosta.guarded.primitives import GuardedPrimitive
from openhosta.guarded.wrapper import Guarded, GuardMetadata, unguard
from openhosta.agent.capability import CapabilityMetadata


# --------------------------------------------------------------------------- #
# Prompt building
# --------------------------------------------------------------------------- #


def _format_type_hint(annotation: Any) -> str:
    """Convert a Python type annotation to a readable string."""
    if annotation is inspect.Parameter.empty:
        return "Any"
    # Handle common typing constructs
    try:
        return str(annotation)
    except Exception:
        return "Any"


def build_infer_prompt(
    func: Any,
    capability_meta: CapabilityMetadata,
    *args: Any,
    **kwargs: Any,
) -> str:
    """Build a structured prompt from a decorated function.

    Extracts the function signature, docstring, and argument values
    to create a prompt that the LLM can execute as a bounded contract.

    Returns
    -------
    str
        The formatted prompt ready for the LLM.
    """
    sig = inspect.signature(func)
    # Convention V5 : utiliser long_description quand disponible,
    # sinon description courte, sinon docstring brute
    doc = (capability_meta.long_description
           or capability_meta.description
           or (func.__doc__ or "")
           ).strip()

    # Build parameter descriptions
    params_desc = []
    for name, param in sig.parameters.items():
        type_hint = _format_type_hint(param.annotation)
        # Get the value from kwargs first, then positional args
        value = kwargs.get(name)
        if value is None:
            param_names = list(sig.parameters.keys())
            try:
                idx = param_names.index(name)
                if idx < len(args):
                    value = args[idx]
            except ValueError:
                pass

        if value is not None:
            params_desc.append(f"- **{name}** (`{type_hint}`): {value!r}")
        else:
            params_desc.append(f"- **{name}** (`{type_hint}`): *[not provided]*")

    # Build return type description
    return_annotation = sig.return_annotation
    if return_annotation is inspect.Signature.empty:
        return_desc = "str"
    else:
        return_desc = _format_type_hint(return_annotation)

    # Construct the prompt
    prompt_lines = [
        "You are a specialized AI function executor. Your task is to execute the following bounded contract:",
        "",
        f"**Function:** `{capability_meta.name or func.__name__}`",
    ]

    # Use long_description (rich prompt) or fall back to short description
    if capability_meta.long_description:
        prompt_lines.append(capability_meta.long_description)
    else:
        prompt_lines.append(f"**Description:** {doc}")

    prompt_lines.append("")
    prompt_lines.append("**Parameters:**")

    if params_desc:
        prompt_lines.extend(params_desc)
    else:
        prompt_lines.append("- No parameters")

    prompt_lines.extend([
        "",
        "**Return type:** " + return_desc,
        "",
        "Execute this function contract. Return ONLY the result in the specified format.",
        "Return no explanations, no markdown code blocks, and no wrapper text.",
    ])

    return "\n".join(prompt_lines)


# --------------------------------------------------------------------------- #
# Backend call
# --------------------------------------------------------------------------- #


@dataclass
class InferenceResult:
    """Encapsulates the result of an LLM inference call.

    Parameters
    ----------
    success: bool
        Whether the inference was successful.
    value: Any
        The parsed and validated result (Guarded[T] when available).
    raw_response: str
        The raw text response from the LLM.
    metadata: GuardMetadata
        Metadata about the inference (tokens, latency, uncertainty).
    error: Exception | None
        The error if the inference failed.
    """
    success: bool
    value: Any = None
    raw_response: str = ""
    metadata: GuardMetadata = field(default_factory=GuardMetadata)
    error: Exception | None = None


def call_backend(
    prompt: str,
    backend_model: Any,
    headers: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
    model_params: dict[str, Any] | None = None,
    timeout: int = 120,
) -> tuple[str, dict]:
    """Call an OpenAI-compatible backend and return the response text.

    Priority chain (lowest → highest):
      1. call_backend defaults (code level)
      2. BackendModel.__init__ (headers, body, model_params, timeout)
      3. @model.infer / direct call (headers, body, model_params, timeout)

    Parameters
    ----------
    prompt: str
        The prompt to send.
    backend_model: BackendModel
        The backend configuration.
    headers: dict[str, str] | None
        Override headers from @model.infer / call-time (highest priority).
    body: dict[str, Any] | None
        Override body fields from @model.infer / call-time (highest priority).
    model_params: dict[str, Any] | None
        Override model params from @model.infer / call-time (highest priority).
    timeout: int
        Request timeout in seconds.

    Returns
    -------
    tuple[str, dict]
        The response text and usage metadata.

    Raises
    ------
    Exception
        If the backend call fails.
    """
    import json as _json

    # --- Merge model params: defaults < BackendModel < infer/call ---
    merged_params: dict[str, Any] = {
        "temperature": 0.1,
        "max_tokens": 4096,
    }
    bp = getattr(backend_model, "model_params", None)
    if bp:
        merged_params.update(bp)
    if model_params:
        merged_params.update(model_params)

    # --- Merge body: defaults < BackendModel < infer/call ---
    payload: dict[str, Any] = {
        "model": backend_model.model_name,
        "messages": [
            {"role": "system", "content": "You are a precise function executor. Return ONLY the result, no explanations."},
            {"role": "user", "content": prompt},
        ],
        **merged_params,
    }
    bb = getattr(backend_model, "body", None)
    if bb:
        payload.update(bb)
    if body:
        payload.update(body)

    # --- Merge timeout: code default < BackendModel < infer/call ---
    bt = getattr(backend_model, "timeout", 120)
    if timeout != 120:
        bt = timeout

    url = backend_model.base_url.rstrip("/") + "/chat/completions"

    # --- Merge headers: defaults < BackendModel < infer/call ---
    req_headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {backend_model.api_key}" if backend_model.api_key else "",
        "User-Agent": "openhosta/5.0",
    }
    bh = getattr(backend_model, "headers", None)
    if bh:
        req_headers.update(bh)
    if headers:
        req_headers.update(headers)

    req = urllib.request.Request(
        url,
        data=_json.dumps(payload).encode("utf-8"),
        headers=req_headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=bt) as resp:
            data = _json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return content, usage
    except urllib.error.HTTPError as e:
        raise Exception(f"Backend HTTP error {e.code}: {e.read().decode('utf-8', errors='replace')}") from e
    except Exception as e:
        raise Exception(f"Backend call failed: {e}") from e


# --------------------------------------------------------------------------- #
# Guarded parsing
# --------------------------------------------------------------------------- #


def parse_guarded(
    raw_text: str,
    return_annotation: Any,
) -> tuple[Any, GuardMetadata]:
    """Parse LLM response into a guarded type.

    Parameters
    ----------
    raw_text: str
        The raw text response from the LLM.
    return_annotation: Any
        The expected return type annotation.

    Returns
    -------
    tuple[Any, GuardMetadata]
        The parsed value (wrapped in Guarded[T]) and associated metadata.
    """
    if return_annotation is inspect.Signature.empty or return_annotation is None:
        # No type constraint, return raw string with basic metadata
        meta = GuardMetadata(
            uncertainty=0.3,
            sources=["llm_inference"],
            llm_logs=[{"raw_length": len(raw_text)}],
        )
        return Guarded(raw_text, meta), meta

    try:
        # Try to parse as JSON first (for structured types)
        try:
            parsed = json.loads(raw_text)
        except (json.JSONDecodeError, ValueError):
            parsed = raw_text

        # Use guard() to validate and wrap
        guarded_value = guard(parsed, target=return_annotation)

        # Unwrap validated value regardless of wrapper type
        if isinstance(guarded_value, Guarded):
            validated = guarded_value.unwrap()
        elif isinstance(guarded_value, GuardedPrimitive):
            validated = guarded_value.unwrap()
        else:
            validated = parsed

        # Always return consistent metadata with sources
        meta = GuardMetadata(
            uncertainty=0.0,
            sources=["llm_inference"],
            llm_logs=[{"raw_length": len(raw_text)}],
        )
        result = Guarded(validated, meta)
        return result, meta
    except Exception as e:
        meta = GuardMetadata(
            uncertainty=1.0,
            logs=[f"Parsing failed: {e}"],
            sources=["llm_inference"],
        )
        raise ValueError(f"Failed to parse LLM response into {return_annotation}: {e}") from e


# --------------------------------------------------------------------------- #
# Main inference pipeline
# --------------------------------------------------------------------------- #


def execute_inference(
    func: Any,
    capability_meta: CapabilityMetadata,
    backend_model: Any,
    *args: Any,
    **kwargs: Any,
) -> InferenceResult:
    """Execute the full inference pipeline.

    1. Build prompt from function signature + args
    2. Call backend LLM
    3. Parse response with guarded types
    4. Return result with metadata

    Parameters
    ----------
    func: Any
        The decorated function (with signature and docstring).
    capability_meta: CapabilityMetadata
        The capability metadata (name, description, tags).
    backend_model: BackendModel
        The backend configuration to use.
    *args: Any
        Positional arguments passed to the capability.
    **kwargs: Any
        Keyword arguments passed to the capability.

    Returns
    -------
    InferenceResult
        The complete result including parsed value, metadata, and any error.
    """
    start_time = time.time()

    # Extract inference-override kwargs (__ prefix to avoid collision with func params)
    infer_headers: dict[str, str] = kwargs.pop("__infer_headers__", {})
    infer_body: dict[str, Any] = kwargs.pop("__infer_body__", {})
    infer_model_params: dict[str, Any] = kwargs.pop("__infer_model_params__", {})
    infer_timeout: int = kwargs.pop("__infer_timeout__", 120)

    try:
        # Step 1: Build prompt
        prompt = build_infer_prompt(func, capability_meta, *args, **kwargs)

        # Step 2: Call backend
        raw_response, usage = call_backend(
            prompt, backend_model,
            headers=infer_headers,
            body=infer_body,
            model_params=infer_model_params,
            timeout=infer_timeout,
        )

        # Step 3: Parse with guarded types
        sig = inspect.signature(func)
        return_annotation = sig.return_annotation

        try:
            parsed_value, metadata = parse_guarded(raw_response, return_annotation)
        except ValueError as e:
            elapsed = (time.time() - start_time) * 1000
            error_meta = GuardMetadata(
                uncertainty=1.0,
                time_consumed=elapsed,
                logs=[str(e)],
                llm_logs=[{"raw_response": raw_response}],
            )
            return InferenceResult(
                success=False,
                raw_response=raw_response,
                metadata=error_meta,
                error=e,
            )

        # Enrich metadata
        elapsed = (time.time() - start_time) * 1000
        metadata.time_consumed = elapsed
        metadata.sources.append("llm_inference")
        metadata.llm_logs.append({
            "model": backend_model.model_name,
            "usage": usage,
            "raw_length": len(raw_response),
        })

        return InferenceResult(
            success=True,
            value=parsed_value,
            raw_response=raw_response,
            metadata=metadata,
        )

    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        error_meta = GuardMetadata(
            uncertainty=1.0,
            time_consumed=elapsed,
            logs=[f"Inference pipeline error: {e}"],
        )
        return InferenceResult(
            success=False,
            metadata=error_meta,
            error=e,
        )


# --------------------------------------------------------------------------- #
# Stub detection
# --------------------------------------------------------------------------- #


def is_stub(func: Any) -> bool:
    """Check if a function has a stub body (only `...` or `pass`).

    Uses AST-based detection for reliability across Python versions.

    Parameters
    ----------
    func: Any
        The function to check.

    Returns
    -------
    bool
        True if the function body is a stub.
    """
    # Built-ins and C extensions have no Python source
    if not hasattr(func, "__code__"):
        return False
    if not hasattr(func, "__code__") or func.__code__ is None:
        return False

    try:
        source = inspect.getsource(func)
        source = textwrap.dedent(source)
        tree = ast.parse(source)
        # Find the function definition in the AST
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                body = node.body
                # Skip leading docstring if present
                effective_body = body
                if (len(body) >= 1 and isinstance(body[0], ast.Expr)
                        and isinstance(body[0].value, ast.Constant)
                        and isinstance(body[0].value.value, str)):
                    effective_body = body[1:]

                # A stub body has exactly one statement after docstring
                if len(effective_body) == 1:
                    stmt = effective_body[0]
                    # `pass`
                    if isinstance(stmt, ast.Pass):
                        return True
                    # `...` (Ellipsis as an Expr statement)
                    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                        if stmt.value.value is ...:
                            return True
                return False
    except (OSError, TypeError, ValueError):
          # Fallback: if we can't get source, use dis to check bytecode
        try:
            import dis
            ops = [instr.opname for instr in dis.get_instructions(func)]
            # A stub has only trivial instructions:
            # - RESUME (entry point)
            # - LOAD_CONST / RETURN_CONST (Ellipsis or None)
            # - RETURN_VALUE / RETURN_CONST (return)
            # - LOAD_FAST / POP_TOP (arg handling)
            # - NOP (no-op)
            trivial_ops = {
                "RESUME", "LOAD_CONST", "RETURN_CONST",
                "RETURN_VALUE", "LOAD_FAST", "POP_TOP", "NOP",
            }
            non_trivial = {op for op in ops if op not in trivial_ops}
            if not non_trivial and len(ops) <= 5:
                # Further check: constants (excluding docstring at co_consts[0])
                # should only be None or Ellipsis
                const_values = func.__code__.co_consts
                # co_consts[0] is the docstring; check remaining constants
                body_consts = const_values[1:] if len(const_values) > 1 else ()
                if all(c is None or c is ... for c in body_consts):
                    return True
        except (AttributeError, TypeError, ImportError):
            pass
    return False
