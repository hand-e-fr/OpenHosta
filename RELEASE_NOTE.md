# Version 1.1 - 09/27/2024

This release introduces significant new features, enhancements, optimizations, and bug fixes to improve the functionality and performance of OpenHosta.

### New Features
- **`example` Function**: Adds examples for a specified hosta-injected function and caches them.
- **`save_examples` Function**: Saves all examples of a hosta-injected function in a JSONL file.
- **`load_examples` Function**: Loads an example file into a cache for a hosta-injected function.
- **`set_prompt` in `PromptManager`**: Automatically changes a prompt in "prompt.json".
- **`suggest` function**: Works the same as the `__suggest__` attributs but in a function

### Changes
- **`suggest` attribute**: Fixed `diagramm` to `diagram`.

### Enhancements
- **`thought` Function**: Automatically guesses its return type with LLM.
- **`suggest` Function**: Returns data from LLM in a dictionary.
- **`emulate` Function**:
  - Now works for class methods.
  - Integrates local variables of the emulated function into the LLM prompt.
  - Includes a verification output to check and convert the output to the specified type if necessary. Supported types include Pydantic models, types from the typing module (List, Dict, Tuple, etc.), and built-in types (dict, int, float, etc.).
  - Added `_last_request` attribute to access the prompt sent to the LLM and `_last_response` to acces the raw message received.
- **Support for Typing Module**: Allows specific return types from the typing module, including List, Dict, Tuple, Set, FrozenSet, Deque, Iterable, Sequence, Mapping, Union, Optional, Literal.
- **Return Type Prediction**: The return type predicted by `thought` is now attached as an attribute (`_return_type`).

### Optimizations
- **`emulate` Prompt**: Removed confidence level, resulting in ~20% speed improvement.
- **Enhanced Prompts**: Added code blocks, separators, and references to the processed function name for `emulate`, `enhance`, `thought`, and `estimate`.

### Bug Fixes
- **`emulate` Function**: 
  - Now decorator-resistant and works in nested functions.
  - now works when emulated function is called inside another one
  - works now with ``lru_cache`` decorator from functools module
- **`config.set_default_model`**: Works correctly with `config.set_default_apiKey`.
- **`thought` Function**: Now accepts multiple arguments.
- **`suggest` and `analytics` Functions**: Now call LLM with `Model` class (`ai_call`).
- **Flask Compatibility**: Added compatibility with Flask.
- Added a loop to find the frame in ``_extend_scope``

### Internal Improvements
- **Functional Tests**: Added for each library feature.
- **Custom Exception Classes**: Added for request and frame errors.
- **Makefile**: Added for cleaning, packaging, and testing.
- **GitHub Workflows**: Added for linting, formatting, and testing on push to dev and main branches.

### Documentation
- **Google Cobal Link**: Integrated into the documentation.
- **Inconsistencies and Errors**: Corrected various documentation issues.

### Performance Metrics
- **`emulate` Function**: Execution time decreased by ~20% despite a slight performance drop since version v1.0.2.
- **`thought` Function**: Execution time increased significantly due to the type prediction system, resulting in a double LLM call.
- **Caching System**: No impact on the execution time of OpenHosta functions.

### Instructions for Update
To update to this version, use the following command:
```sh
pip install --upgrade OpenHosta
```
Remember to delete `__hostacache__` folders to avoid version conflicts.

### Acknowledgements
Thank you to all contributors for your valuable feedback and contributions: @ramosleandre, @MerlinDEVILLARD, @WilliamJlvt, and @battmanux.

---