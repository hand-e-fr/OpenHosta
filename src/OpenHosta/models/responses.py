"""Structured tool-calling primitives returned by `Model.respond(...)`.

These mirror the OpenAI tool-calling shape but stay framework-agnostic so that
HostaAgent (or any caller) can drive a ReAct loop without touching raw API dicts.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ToolCall:
    """A single tool invocation requested by the model (args already parsed)."""
    id: str
    name: str
    args: Dict[str, Any]


@dataclass
class ToolResult:
    """The outcome of running a tool, fed back to the model on the next turn."""
    id: str
    content: str
    is_error: bool = False


@dataclass
class ModelResponse:
    """One assistant turn: free text and/or a list of tool calls."""
    text: Optional[str]
    tool_calls: List[ToolCall] = field(default_factory=list)
    raw_calls: List[Any] = field(default_factory=list)  # original payload, round-tripped in messages
    finish_reason: str = "stop"


def parse_tool_args(raw: Any) -> Dict[str, Any]:
    """Tolerantly parse a tool-call ``arguments`` payload into a dict.

    Tool-call args arrive as JSON strings, occasionally malformed. We try, in
    order: pass-through (already a dict), ``json.loads``, then OpenHosta's
    Guarded dict cascade (which itself falls back through literal-eval and
    heuristics). On total failure we return ``{}`` so the tool is still called —
    the resulting error becomes the tool result and the model self-corrects on
    the next turn.
    """
    if isinstance(raw, dict):
        return raw
    if raw is None:
        return {}
    text = raw if isinstance(raw, str) else str(raw)
    if not text.strip():
        return {}
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except (json.JSONDecodeError, ValueError):
        pass
    try:
        from ..guarded.subclassablecollections import GuardedDict
        res = GuardedDict.attempt(text)
        if res.success and isinstance(res.data, dict):
            return res.data
    except Exception:
        pass
    return {}
