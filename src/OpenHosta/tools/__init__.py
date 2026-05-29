"""Tool-calling support for OpenHosta.

A tool is *any* callable with type hints and a docstring. `@tool` only attaches
optional metadata; `tool_to_schema` turns a callable into an OpenAI-compatible
function schema. The loop that actually calls tools lives in HostaAgent.
"""
from .decorator import ToolMeta, tool
from .schema import tool_to_schema

__all__ = ("tool", "ToolMeta", "tool_to_schema")
