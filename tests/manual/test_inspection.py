
from OpenHosta import emulate, Guarded, conversation, readable, markdown, print_last_prompt
import os

# Ensure .env is loaded
from OpenHosta import reload_dotenv
reload_dotenv()

def test_inspection():
    def get_age(name: str) -> Guarded[int]:
        """Return the age of the person."""
        return emulate()

    print("--- Calling get_age('John') ---")
    age = get_age("John")
    print(f"Result: {age} (type: {type(age)})")
    
    print("\n--- Testing conversation(age) ---")
    conversation(age)

    print("\n--- Testing readable(age) ---")
    r = readable(age)
    print(f"Readable: {r}")

    print("\n--- Testing markdown(age) ---")
    m = markdown(age)
    print(f"Markdown:\n{m}")

    print("\n--- Testing stability: GuardedInt(readable(age)) ---")
    from OpenHosta.guarded import GuardedInt
    age_copy = GuardedInt(readable(age))
    print(f"Copy: {age_copy} (type: {type(age_copy)})")
    assert age_copy == age

    print("\n--- SUCCESS ---")

if __name__ == "__main__":
    test_inspection()
