import pytest
from OpenHosta import emulate, config
from OpenHosta.core.cost_tracker import track_costs
from OpenHosta.core.audit import register_audit_callback, unregister_audit_callback, AuditEvent

def test_cost_tracker():
    def say_hello(name: str) -> str:
        """
        Say hello to the given name.
        """
        return emulate()

    with track_costs() as tracker:
        res1 = say_hello("Alice")
        res2 = say_hello("Bob")
        
    assert tracker.calls == 2, f"Expected 2 calls, got {tracker.calls}"
    assert tracker.total_tokens > 0, "Expected total_tokens to be accumulated."
    assert "Hello" in res1, f"Expected 'Hello' in {res1}"
    assert "Hello" in res2, f"Expected 'Hello' in {res2}"


def test_audit_callbacks():
    events_caught = []

    def my_callback(event: AuditEvent):
        events_caught.append(event)
        
    register_audit_callback(my_callback)
    
    def simple_math() -> int:
        """
        Return 2+2
        """
        return emulate()
        
    try:
        res = simple_math()
        assert res == 4, f"Expected 4, got {res}"
        
        # We should have caught an emulate_success event
        assert len(events_caught) > 0, "Expected at least one audit event to be caught."
        success_events = [e for e in events_caught if e.event_type == "emulate_success"]
        assert len(success_events) > 0, "Expected a emulate_success event."
        
    finally:
        unregister_audit_callback(my_callback)
