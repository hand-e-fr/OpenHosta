from enum import StrEnum
# Assumed 'UncertaintyError' needs to be imported to be caught
from OpenHosta import emulate, safe, UncertaintyError

class NextStep(StrEnum):
    """Enumeration defining the possible git commands."""
    GIT_PUSH = "git push"
    GIT_COMMIT = "git commit"
    GIT_STATUS = "git status"
    GIT_FETCH = "git fetch"
    GIT_PULL = "git pull"

def get_next_step(command: str) -> NextStep:
    """
    Determines the next logical git step based on the provided command.
    Returns a NextStep enum.
    """
    return emulate()

def get_random_string() -> str:
    """
    Generates a random sentence.
    """
    return emulate()

if __name__ == "__main__":
    # Initialize the safe context with a strict uncertainty threshold
    with safe(acceptable_cumulated_uncertainty=1e-5) as safety_context:
        try:
            print("--- Starting Safe Execution ---\n")

            # 1. Cumulated uncertainty loop
            # Each iteration adds to the total uncertainty of the context
            for i in range(3):
                next_step = get_next_step("git commit -m 'Initial commit'")
                
                print(f"[Iteration {i+1}] UUID: {safety_context.uuid}")
                print(f"Status: {safety_context.cumulated_uncertainty} / {safety_context.acceptable_cumulated_uncertainty}")

            print("\n--- Triggering High Uncertainty ---\n")

            # 2. High uncertainty trigger
            # The prompt 'git is forbidden here' is ambiguous/unexpected, 
            # which should cause the model's uncertainty to cross the threshold.
            next_step = get_next_step("git is forbidden here")

            # 3. Standard generation
            # This part might not be reached if the previous line raises an error.
            sentence = get_random_string()
            print(f"Generated sentence: {sentence}")

        except UncertaintyError as e:
            print(f"(!) Caught expected UncertaintyError:\n    {e}")
            # Print the trace to debug where the uncertainty spiked
            print(f"Trace: {safety_context.trace}")

        finally:
            print("\n--- Execution Summary ---")
            print(f"Final Context UUID: {safety_context.uuid}")
            print(f"Final Uncertainty:  {safety_context.cumulated_uncertainty} / {safety_context.acceptable_cumulated_uncertainty}")