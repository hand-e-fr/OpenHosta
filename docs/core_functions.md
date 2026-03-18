# Core Functions

This document covers the primary functions used to interact with LLMs in OpenHosta.

## `emulate`
The `emulate` function is the main feature. It uses the function's prototype and docstring as a prompt to emulate the behavior using AI.

```python
from OpenHosta import emulate

def translate(text: str, language: str) -> str:
    """Translates the text into the specified language."""
    return emulate()

print(translate("Hello", "French"))
```

## `emulate` (Asynchronous Mode)
Useful for web applications or multiple parallel calls.

```python
import asyncio
from OpenHosta.asynchrone import emulate

async def capitalize_cities(sentence: str) -> str:
    """Capitalize the first letter of all city names in a sentence."""
    return await emulate()

print(asyncio.run(capitalize_cities("je suis allé à paris")))
```

## `closure`
Replicates lambda functions.

```python
from OpenHosta import closure

is_masculine = closure("Is it a masculine name?")
print(is_masculine("John"))  # True
```

## `ask`
A simple LLM call without OpenHosta's specific meta-prompt.

```python
from OpenHosta import ask

print(ask("Do you know about scikit-learn?"))
```

## Reasoning Models
For reasoning models (like DeepSeek-R1 or specific local models), OpenHosta automatically removes the reasoning part before casting the output.
