## OpenHosta v1.1.1 - 10/07/24

This patch focuses on performance enhancements and bug fixes related to prompt handling and output typing.

### Features
- Introduced the `_last_request` attribute to the `Model` object for enhanced tracking.

### Optimization
- Streamlined the `emulate` user prompt by limiting it to the function call string and moving additional information to the system prompt.
- Enhanced the structure of the `emulate` prompt with markdown headers.
- Eliminated unnecessary sentences such as confidence levels and transitions for a more concise output.

### Internal
- Refactored the prompt-building function within `emulate` for improved maintainability.
- Removed the validate function in the LLM call response handler to simplify the codebase.

### Fixes
- Added code block syntax for clearer function definitions.
- Re-added the `diagramm` attribute (now deprecated) for backward compatibility.
- Explicitly included a neutral response (None) in the `emulate` prompt to handle edge cases.
