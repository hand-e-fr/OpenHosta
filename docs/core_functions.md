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

## `emulate_iterator`
Returns a lazily evaluated generator/iterator. It yields elements one-by-one directly from the underlying LLM streams, vastly reducing latency for list generations.

> Note: tested mainly with qwen3:8b-instruct served by ollama

```python
from OpenHosta import emulate_iterator

def generate_ideas(topic: str) -> list[str]:
    """Yield multiple creative ideas based on the topic."""
    return emulate_iterator()

for idea in generate_ideas("Open Source Marketing"):
    print(idea) # Starts printing before the entire list is fully generated
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
