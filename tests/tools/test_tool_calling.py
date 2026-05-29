"""Offline tests for the tool-calling MVP (no live API key required).

Mirrors the acceptance test in HostaAgent's blueprint (03_OPENHOSTA_TOOLS.md):
a tool round-trips into a schema and the model parses a tool call back out.
The HTTP layer is monkeypatched so these run anywhere.
"""
import asyncio
from enum import Enum
from typing import Optional

import pytest

import OpenHosta.models.OpenAICompatible as oc
from OpenHosta import (
    ModelResponse,
    OpenAICompatibleModel,
    ToolCall,
    tool,
    tool_to_schema,
)
from OpenHosta.models.responses import parse_tool_args


@tool
def add(a: int, b: int) -> int:
    "Add two integers."
    return a + b


class _FakeHTTPResponse:
    status_code = 200
    headers: dict = {}

    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def _patch_post(monkeypatch, payload):
    monkeypatch.setattr(oc.requests, "post", lambda *a, **k: _FakeHTTPResponse(payload))


def _model():
    # localhost base_url avoids the OpenAI api-key requirement in _generate_without_retry
    return OpenAICompatibleModel(model_name="x", base_url="http://localhost:11434/v1", api_key="k")


def test_tool_to_schema_basic():
    schema = tool_to_schema(add)
    assert schema["type"] == "function"
    fn = schema["function"]
    assert fn["name"] == "add"
    assert fn["description"] == "Add two integers."
    assert fn["parameters"]["properties"] == {"a": {"type": "integer"}, "b": {"type": "integer"}}
    assert fn["parameters"]["required"] == ["a", "b"]


def test_tool_to_schema_optional_and_default():
    def search(query: str, limit: int = 10, exact: Optional[bool] = None) -> str:
        "Search."
        return ""

    props = tool_to_schema(search)["function"]["parameters"]
    assert props["properties"]["query"] == {"type": "string"}
    assert props["properties"]["limit"] == {"type": "integer"}
    assert props["properties"]["exact"] == {"type": "boolean"}
    assert props["required"] == ["query"]  # only the param with no default


def test_tool_to_schema_enum_and_list():
    class Color(Enum):
        RED = "red"
        BLUE = "blue"

    def paint(colors: list[str], primary: Color) -> str:
        "Paint."
        return ""

    props = tool_to_schema(paint)["function"]["parameters"]["properties"]
    assert props["colors"] == {"type": "array", "items": {"type": "string"}}
    assert props["primary"] == {"type": "string", "enum": ["red", "blue"]}


def test_tool_to_schema_literal_with_enum_members_is_json_serializable():
    import json
    from typing import Literal

    class Status(Enum):
        ACTIVE = "active"
        DONE = "done"

    def setp(state: Literal[Status.ACTIVE, Status.DONE]) -> str:
        "Set state."
        return ""

    schema = tool_to_schema(setp)
    state = schema["function"]["parameters"]["properties"]["state"]
    assert state == {"enum": ["active", "done"], "type": "string"}
    json.dumps(schema)  # must not raise (enum members were unwrapped to .value)


def test_tool_to_schema_numeric_enum_infers_integer_type():
    class Priority(Enum):
        LOW = 1
        HIGH = 2

    def prioritize(p: Priority) -> str:
        "Prioritize."
        return ""

    prop = tool_to_schema(prioritize)["function"]["parameters"]["properties"]["p"]
    assert prop == {"enum": [1, 2], "type": "integer"}


def test_tool_to_schema_homogeneous_and_heterogeneous_tuple():
    from typing import Tuple

    def f(pair: Tuple[int, int], mixed: Tuple[int, str], variadic: Tuple[str, ...]) -> str:
        "Tuples."
        return ""

    props = tool_to_schema(f)["function"]["parameters"]["properties"]
    assert props["pair"] == {"type": "array", "items": {"type": "integer"}}
    assert props["variadic"] == {"type": "array", "items": {"type": "string"}}
    assert props["mixed"] == {"type": "array"}  # heterogeneous -> no misleading items


def test_respond_parses_tool_call(monkeypatch):
    _patch_post(monkeypatch, {
        "choices": [{
            "finish_reason": "tool_calls",
            "message": {
                "content": None,
                "tool_calls": [{
                    "id": "call_1",
                    "type": "function",
                    "function": {"name": "add", "arguments": '{"a": 2, "b": 3}'},
                }],
            },
        }],
    })
    r = asyncio.run(_model().respond(
        "You answer math.",
        [{"role": "user", "content": "What is 2+3? Use the tool."}],
        tools=[tool_to_schema(add)],
    ))
    assert isinstance(r, ModelResponse)
    assert r.tool_calls and isinstance(r.tool_calls[0], ToolCall)
    assert r.tool_calls[0].name == "add"
    assert r.tool_calls[0].args == {"a": 2, "b": 3}  # validated/parsed
    assert r.raw_calls[0]["id"] == "call_1"
    assert r.finish_reason == "tool_calls"


def test_respond_plain_text(monkeypatch):
    _patch_post(monkeypatch, {
        "choices": [{"finish_reason": "stop", "message": {"content": "Paris"}}],
    })
    r = asyncio.run(_model().respond("Geography.", [{"role": "user", "content": "Capital of France?"}]))
    assert r.text == "Paris"
    assert r.tool_calls == []


@pytest.mark.parametrize("raw,expected", [
    ('{"a": 1}', {"a": 1}),
    ("{'a': 1}", {"a": 1}),         # single quotes -> Guarded cascade
    ("", {}),
    (None, {}),
    ({"x": 2}, {"x": 2}),           # already a dict
    ("not json at all", {}),         # unparseable -> empty (tool errors, model self-corrects)
])
def test_parse_tool_args_tolerant(raw, expected):
    assert parse_tool_args(raw) == expected
