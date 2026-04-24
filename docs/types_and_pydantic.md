# Types & Pydantic Integration

OpenHosta natively supports Python's typing modules and Pydantic V2 definitions out-of-the-box.

## Supported Types
You can use standard Python types as the return type for an `emulate` function. Supported types include `List`, `Dict`, `Tuple`, `Set`, `FrozenSet`, `Deque`, `Iterable`, `Sequence`, `Mapping`, `Union`, `Optional`, and `Literal`.

Supported built-in types include `int`, `float`, `str`, `bool`.

Starting from **OpenHosta 4.1**, you can also return executable code using `Callable`.

See [Generative Functions & Callable](callables.md) for more details.

```python
from OpenHosta import emulate
from typing import Dict, Tuple, List

def analyze_text(text: str) -> Dict[str, List[Tuple[int, str]]]:
    """Analyze text to map each word to a list of tuples containing word length and word."""
    return emulate()

analysis = analyze_text("Hello, World!")
```

## Pydantic Output Validation
The most deterministic way to control the output structure is using Pydantic. OpenHosta will format the prompt to request JSON that matches the Pydantic schema and then cast the resulting JSON back into Pydantic models.

```python
from pydantic import BaseModel
from OpenHosta import emulate

class Person(BaseModel):
    name: str
    age: int

def find_first_name(sentence: str) -> Person:
    """Finds the name and age of a person in the text."""
    return emulate()

print(find_first_name("The captain's age is one year more than the first officer's age. The first officer is 30 years old"))
# Person(name='first officer', age=30)
```

## Guarded Types
In OpenHosta V4, **Guarded Types** provide a robust abstraction for ensuring type structural and semantic validitiy behind the scenes. This handles strict validation rules during extraction pipelines.

See [Guarded Types Overview](guarded.md) for more details.

## Python 3.12 Type Aliases

Starting from Python 3.12, the `type` statement allows creating type aliases natively (PEP 695).
OpenHosta supports this syntax out-of-the-box and will accurately map your aliases into the LLM prompt.

```python
from typing import Literal
from dataclasses import dataclass
from OpenHosta import emulate

type RegimeMatrimonial = Literal["Marié", "PACS", "Concubin"]

@dataclass
class Family:
    name: str
    status: RegimeMatrimonial

def identify_family(document: str) -> Family:
    """Extract family information"""
    return emulate()
```

OpenHosta will correctly display the alias name `RegimeMatrimonial` in the `Family` structure definition and document the alias itself separately in the prompt to provide clear context to the LLM.
