"""Tests for events module — EventType, Event, EventStream.

DEF-EXEC-EVENT-001 — Canonical event types for task, trace and metric emission
"""

from __future__ import annotations

import pytest

from openhosta.agent import Event, EventStream, EventType

# ============================================================================
# TestEventType
# ============================================================================


class TestEventType:
    def test_all_event_types_exist(self) -> None:
        expected = {
            "TASKLIST_CREATED",
            "TASKLIST_UPDATED",
            "TASKLIST_REVIDED",
            "TASK_STARTED",
            "TASK_PROGRESSED",
            "TASK_COMPLETED",
            "TASK_FAILED",
            "TASK_CANCELLED",
            "INCIDENT_RECORDED",
            "METRIC_RECORDED",
        }
        actual = {e.name for e in EventType}
        assert actual == expected

    def test_count(self) -> None:
        assert len(EventType) == 10  # noqa: PLR2004


# ============================================================================
# TestEventCreation
# ============================================================================


class TestEventCreation:
    def test_defaults(self) -> None:
        e = Event(event_type=EventType.TASK_STARTED)
        assert e.event_type == EventType.TASK_STARTED
        assert isinstance(e.event_id, str)
        assert len(e.event_id) == 36  # UUID-4
        assert isinstance(e.timestamp, float)
        assert e.session_id == ""
        assert e.tasklist_id is None
        assert e.step_id is None
        assert e.payload == {}
        assert e.metadata == {}

    def test_custom_fields(self) -> None:
        e = Event(
            event_type=EventType.TASK_COMPLETED,
            session_id="s1",
            tasklist_id="tl1",
            step_id="step1",
            payload={"duration_sec": 42},
        )
        assert e.session_id == "s1"
        assert e.tasklist_id == "tl1"
        assert e.step_id == "step1"
        assert e.payload["duration_sec"] == 42

    def test_frozen(self) -> None:
        e = Event(event_type=EventType.TASK_STARTED)
        with pytest.raises(AttributeError):
            e.session_id = "x"  # type: ignore[assignment]

    def test_event_ids_are_unique(self) -> None:
        e1 = Event(event_type=EventType.TASK_STARTED)
        e2 = Event(event_type=EventType.TASK_STARTED)
        assert e1.event_id != e2.event_id


# ============================================================================
# TestEventHelpers
# ============================================================================


class TestEventHelpers:
    def test_with_metadata(self) -> None:
        e = Event(event_type=EventType.TASK_STARTED, metadata={"k": "v"})
        e2 = e.with_metadata(correlation_id="c1", trace_id="t1")
        assert e.metadata == {"k": "v"}  # original unchanged
        assert e2.metadata == {"k": "v", "correlation_id": "c1", "trace_id": "t1"}

    def test_with_metadata_overwrites(self) -> None:
        e = Event(event_type=EventType.TASK_STARTED, metadata={"k": "v"})
        e2 = e.with_metadata(k="new")
        assert e2.metadata["k"] == "new"

    def test_is_task_event_true(self) -> None:
        for et in (
            EventType.TASK_STARTED,
            EventType.TASK_PROGRESSED,
            EventType.TASK_COMPLETED,
            EventType.TASK_FAILED,
            EventType.TASK_CANCELLED,
        ):
            e = Event(event_type=et)
            assert e.is_task_event is True, f"Failed for {et.name}"

    def test_is_task_event_false(self) -> None:
        e = Event(event_type=EventType.TASKLIST_CREATED)
        assert e.is_task_event is False

    def test_is_tasklist_event_true(self) -> None:
        for et in (
            EventType.TASKLIST_CREATED,
            EventType.TASKLIST_UPDATED,
            EventType.TASKLIST_REVIDED,
        ):
            e = Event(event_type=et)
            assert e.is_tasklist_event is True, f"Failed for {et.name}"

    def test_is_tasklist_event_false(self) -> None:
        e = Event(event_type=EventType.TASK_STARTED)
        assert e.is_tasklist_event is False

    def test_is_terminal_task_event(self) -> None:
        for et in (
            EventType.TASK_COMPLETED,
            EventType.TASK_FAILED,
            EventType.TASK_CANCELLED,
        ):
            e = Event(event_type=et)
            assert e.is_terminal_task_event is True, f"Failed for {et.name}"

        e = Event(event_type=EventType.TASK_STARTED)
        assert e.is_terminal_task_event is False

    def test_is_positive(self) -> None:
        for et in (
            EventType.TASK_COMPLETED,
            EventType.TASK_STARTED,
            EventType.TASK_PROGRESSED,
            EventType.TASKLIST_CREATED,
            EventType.TASKLIST_UPDATED,
        ):
            e = Event(event_type=et)
            assert e.is_positive is True, f"Failed for {et.name}"

        e = Event(event_type=EventType.TASK_FAILED)
        assert e.is_positive is False

        e = Event(event_type=EventType.INCIDENT_RECORDED)
        assert e.is_positive is False


# ============================================================================
# TestEventStream
# ============================================================================


class TestEventStreamInit:
    def test_empty(self) -> None:
        stream = EventStream(stream_id="stream1")
        assert stream.is_empty is True
        assert stream.count == 0
        assert stream.last_event is None

    def test_append(self) -> None:
        stream = EventStream(stream_id="s1")
        e = Event(event_type=EventType.TASK_STARTED)
        stream2 = stream.append(e)
        assert stream.is_empty is True  # original unchanged
        assert stream2.count == 1
        assert stream2.last_event == e

    def test_append_multiple(self) -> None:
        stream = EventStream(stream_id="s1")
        e1 = Event(event_type=EventType.TASKLIST_CREATED)
        e2 = Event(event_type=EventType.TASK_STARTED)
        stream = stream.append(e1)
        stream = stream.append(e2)
        assert stream.count == 2
        assert stream.last_event == e2

    def test_stream_id_preserved(self) -> None:
        stream = EventStream(stream_id="my-id")
        e = Event(event_type=EventType.TASK_STARTED)
        s2 = stream.append(e)
        assert s2.stream_id == "my-id"

    def test_frozen(self) -> None:
        stream = EventStream(stream_id="s1")
        with pytest.raises(AttributeError):
            stream.stream_id = "x"  # type: ignore[assignment]


class TestEventStreamFilters:
    def _make_stream(self) -> EventStream:
        s = EventStream(stream_id="s")
        s = s.append(Event(event_type=EventType.TASKLIST_CREATED, session_id="a"))
        s = s.append(Event(event_type=EventType.TASK_STARTED, session_id="a", step_id="x"))
        s = s.append(Event(event_type=EventType.TASK_COMPLETED, session_id="a", step_id="x"))
        s = s.append(Event(event_type=EventType.TASK_STARTED, session_id="b", step_id="y"))
        s = s.append(Event(event_type=EventType.TASK_FAILED, session_id="b", step_id="y"))
        return s

    def test_filter_by_type(self) -> None:
        s = self._make_stream()
        filtered = s.filter_by_type(EventType.TASK_STARTED)
        assert filtered.count == 2
        assert filtered.stream_id == "s"

    def test_filter_by_session(self) -> None:
        s = self._make_stream()
        filtered = s.filter_by_session("a")
        assert filtered.count == 3

    def test_filter_by_step(self) -> None:
        s = self._make_stream()
        filtered = s.filter_by_step("y")
        assert filtered.count == 2

    def test_filter_empty_result(self) -> None:
        s = self._make_stream()
        filtered = s.filter_by_session("z")
        assert filtered.is_empty is True

    def test_filter_returns_new_stream(self) -> None:
        s = self._make_stream()
        filtered = s.filter_by_type(EventType.TASK_STARTED)
        assert filtered is not s
        assert s.count == 5

    def test_timestamp_order(self) -> None:
        stream = EventStream(stream_id="time-test")
        e1 = Event(event_type=EventType.TASK_STARTED, timestamp=100.0)
        e2 = Event(event_type=EventType.TASK_COMPLETED, timestamp=200.0)
        stream = stream.append(e1)
        stream = stream.append(e2)
        assert stream.events[0].timestamp < stream.events[1].timestamp
