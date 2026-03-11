# Safe Context & Uncertainty

When using LLMs, it's common to encounter situations where the model produces uncertain or ambiguous responses. OpenHosta provides a "safe context" to handle ambiguity without breaking your code or returning unhandled exceptions deep in the stack.

## `safe` Context Manager

You can define specific conditions under which the model should respond securely or limit the `cumulated_uncertainty` threshold.

```python
from enum import StrEnum
from OpenHosta import emulate, safe, UncertaintyError

class NextStep(StrEnum):
    GIT_PUSH = "git push"
    GIT_COMMIT = "git commit"
    GIT_STATUS = "git status"

def get_next_step(command: str) -> NextStep:
    """Determines the next logical git step based on the provided command."""
    return emulate()

if __name__ == "__main__":
    with safe(acceptable_cumulated_uncertainty=1e-5) as safety_context:
        try:
            for i in range(3):
                next_step = get_next_step("git commit -m 'Initial commit'")
                
            # Trigger high uncertainty 
            next_step = get_next_step("git is forbidden here")

        except UncertaintyError as e:
            print(f"Caught expected UncertaintyError: {e}")
```
Handling errors securely guarantees that unexpected hallucinated output won't propagate logic bugs in production scripts.
