import time
import json
from typing import Any, Callable



def audit_log(event_type: str, details: dict):
    """
    Logs structured information to stdout if audit mode is enabled.
    """
    from ..defaults import config
    if not config.AUDIT_MODE:
        return

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    log_entry = {
        "timestamp": timestamp,
        "event_type": event_type,
        "details": details
    }
    
    # Prefix to easily grep these logs
    print(f"[OPENHOSTA_AUDIT] {json.dumps(log_entry, default=str)}")


class AuditEvent:
    def __init__(self, event_type: str, details: dict):
        self.event_type = event_type
        self.details = details
        self.timestamp = time.time()
        
    def __str__(self):
        return f"{self.event_type}: {self.details}"

_audit_callbacks = []

def register_audit_callback(callback: Callable[[AuditEvent], Any]):
    """
    Register a callback to receive audit events programmatically.
    """
    _audit_callbacks.append(callback)

def unregister_audit_callback(callback: Callable[[AuditEvent], Any]):
    if callback in _audit_callbacks:
        _audit_callbacks.remove(callback)

def trigger_audit_event(event_type: str, details: dict):
    """
    Trigger both console audit logging and any registered callbacks
    """
    audit_log(event_type, details)
    
    event = AuditEvent(event_type, details)
    for callback in _audit_callbacks:
        try:
            callback(event)
        except Exception as e:
             # Do not let callbacks break the main execution flow
            print(f"[OPENHOSTA_AUDIT_WARNING] Audit callback {callback} failed: {e}")
