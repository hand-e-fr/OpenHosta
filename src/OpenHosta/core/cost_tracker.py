import contextvars
from contextlib import contextmanager
from typing import Dict

@contextmanager
def track_costs():
    """
    Context manager to track LLM usage costs (tokens) during execution.
    It captures the tokens used by any OpenHosta calls made within its context.
    """
    tracker = CostTracker()
    token = _current_cost_tracker.set(tracker)
    try:
        yield tracker
    finally:
        _current_cost_tracker.reset(token)


class CostTracker:
    def __init__(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.calls = 0

    def add_usage(self, usage: Dict):
        """Add usage dict returned by an OpenAI-compatible API to the tracker."""
        if not usage:
            return
            
        self.prompt_tokens += usage.get("prompt_tokens", 0)
        self.completion_tokens += usage.get("completion_tokens", 0)
        self.total_tokens += usage.get("total_tokens", 0)
        self.calls += 1

    def __str__(self):
        return f"CostTracker(calls={self.calls}, prompt_tokens={self.prompt_tokens}, completion_tokens={self.completion_tokens}, total_tokens={self.total_tokens})"

_current_cost_tracker: contextvars.ContextVar[CostTracker] = contextvars.ContextVar("current_cost_tracker", default=None)

def get_current_cost_tracker() -> CostTracker | None:
    return _current_cost_tracker.get()
