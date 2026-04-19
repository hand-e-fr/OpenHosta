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

## `emulate_async`
Useful for web applications, heavy IO, or executing multiple LLM calls in parallel without blocking the main event loop.

```python
import asyncio
from OpenHosta import emulate_async

async def capitalize_cities(sentence: str) -> str:
    """Capitalize the first letter of all city names in a sentence."""
    return await emulate_async()

print(asyncio.run(capitalize_cities("je suis allé à paris")))
```

## `emulate_variants`
Explores the LLM's probability distribution to generate independent, alternative responses (variants) based on token logprobs. It is ideal for exploring uncertainty or generating diverse candidates from a single prompt.

It automatically adapts to the return type annotation:
- If `-> list[T]`: Returns a fully resolved list of variants.
- If `-> Iterator[T]`: Returns a generator that yields variants as they are found.

```python
from typing import Iterator
from OpenHosta import emulate_variants

# Returns a list of variants once all are found
def list_variants(topic: str) -> list[str]:
    """Suggest three alternative creative names for a project."""
    return emulate_variants(min_probability=1e-2)

# Yields variants one by one
def stream_variants(topic: str) -> Iterator[str]:
    """Yield multiple alternative titles based on the topic."""
    yield from emulate_variants(min_probability=1e-2)

for variant in stream_variants("Open Source Marketing"):
    print(variant)
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
