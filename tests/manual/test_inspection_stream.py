
from OpenHosta import emulate, Guarded, conversation, readable, markdown
from typing import Iterator
import os

# Ensure .env is loaded
from OpenHosta import reload_dotenv
reload_dotenv()

def test_inspection_stream():
    def get_ages(names: list[str]) -> Iterator[Guarded[int]]:
        """Return the ages of the persons."""
        yield from emulate()

    print("--- Calling get_ages(['John', 'Jane']) ---")
    ages = list(get_ages(['John', 'Jane']))
    
    for i, age in enumerate(ages):
        print(f"\n--- Result {i}: {age} (type: {type(age)}) ---")
        
        print(f"\n--- conversation(age) for result {i} ---")
        conversation(age)
        
        print(f"\n--- readable(age): {readable(age)} ---")
        print(f"\n--- markdown(age):\n{markdown(age)} ---")

    print("\n--- SUCCESS ---")

if __name__ == "__main__":
    test_inspection_stream()
