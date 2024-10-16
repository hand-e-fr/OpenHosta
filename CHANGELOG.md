# Changelog

All significant changes to this project will be documented in this file.

---

## **v1.3.0**

- **Internal**
  - Added `py.typed` file for linter
  - Refacto the project's structure

## **v1.2.0** - 10/14/2024

### **New Features**

- **`predict` Function**  
  The `predict` function is now available, allowing you to create internal models—currently supporting linear regression—based on user-provided training data. This simplifies model generation without relying on external APIs. Key functionalities include:
  - **`.retrain`**: Retrain models with specified parameters.
  - **`.continue_train`**: Continue training with existing model weights.
  - **`.emulate`**: Run predictions through an LLM or create a model directly using internal linear regression based on training data.

- **TrainingSet Management**  
  Manage training datasets effortlessly with new tools:
  - **`.visualize`**: Inspect current data visually.
  - **`.add`**: Add new examples.

### **Enhancements**

- **Expanded Dataset Support**:  
  `load_training_example` (previously `load_examples`) supports JSON, JSONL, and CSV formats for easier integration.

- **Verbose Mode in `predict`**:  
  Track detailed model training and define target losses with `get_loss`.

---
## **v1.1.1** 10/07/24

- **Features**
  - Added `_last_request` attributs to the `Model` object

- **Optimization**
  - Reduce the `emulate`'s user prompt to only the function call string and move the rest in the system prompt.
  - Added markdow header in `emulate` prompt and enhance strucure 
  - Remove unecessary setence like confidence level and transition

- **Internal**
  - Refacto the prompt building function in `emulate`
  - Remove the validate function in LLM call response handler

- **Fixes**
  - Added code block syntax for the function definition.
  - Re-added `diagramm` attributs but decrepated
  - Added explicitly a neutral response in the `emulate` prompt (None)

## **v1.1-rc4** 09/27/24

- **Feature**
  - Added `suggest` function. Works the same as the `__suggest__` attributs but in a function

- **Doc**
  - Many inconsistencies and errors corrected.

- **Internal**
  - Added Github workflows for linting, formating and testing when pushing to dev and main

- **Fixes**
  - `suggest` attribute `diagramm` is now `diagram`
  
## **v1.1-rc3** 09/26/23

- **Fixes**
  - `emulate` now works when emulated function is called inside another one
  - `emulate` works now with `lru_cache` decorator from `functools` module 

- **Internal**
  - Added custom Exception classes for request and frame errors.
  - Added a loop to find the frame in `_extend_scope`
  - Added a Makefile for cleaning and packaging and tests
---

## **v1.1** 09/13/2024

- **Fixes**
  - the `emulate` function is now decorator-resistant.
  - The function `config.set_default_model` works now w/ `config.set_default_apiKey`
  - `thought` function now accept multiple arguments
  - `suggest` and `analytics` call now th LLM with `Model` class (`ai_call`)
  - `emulate` works now in a nested function.
  - Added Flask compatibility
  
- **Enhancement**
  - the `thought` function guess automatically his return type with LLM
  - `suggest` return now his data returned by LLM in a dict
  - `emulate` works now for class methods
  - `emulate` now integrate locals variable of emulated function to the LLM prompt.
  - `_hostacache_` are now available for function infos storage
  - Added support for the **typing** module: You can now use specific return types from the typing module, including [List, Dict, Tuple, Set, FrozenSet, Deque, Iterable, Sequence, Mapping, Union, Optional, Literal].
  - `emulate` now includes a verification output that checks and converts the output to the specified type if necessary. Supported types include **Pydantic** models, all types from the **typing** module mentioned above, as well as built-in types such as `dict`, `int`, `float`, `str`, `list`, `set`, `frozenset`, `tuple`, and `bool`.
    - The `complex` type is not supported. If you need to use complex numbers, please pass them as a `tuple` and manually convert them after processing.
  -  The return type predicted by `thought` is now attached as an attribute to the object created: `_return_type`.
  -  Added a `_last_request` attribute to an emulated function giving access to the prompt sent to the LLM.

- **Features**
  - `example` function that can add some example for a specified hosta-injected function (inside or outside it) and add it to the cache
  - `save_examples` function that can save in a JSONL file all he example of an hosta-injected function
  - `load_examples` function that can load an example file an a cache for an hosta-injected function
  - `set_prompt` in `PromptManager` enables to change automatically a prompt un "prompt.json"

- **Optimization**
  - `emulate` prompt changed: confidence level removed: (~20% speed gained) (`emulate`: v1.1)
  - All prompt enhanced: added code block, separator and reference to the name of the processed function (`emulate`: v1.2, `enhance` v1.2, `thought`: v1.1, `estimate`: v1.1)

- **Internal**
  - Functional tests have been added for each of the library's features

- **Doc**
  - Documentation now integrates Google Cobal link

---

## **v1.0** 08/29/2024:

- **Features**
  - Function *emulate* to emulate a function by LLM.
  - Pydantic typing compatibility with *emulate*.
  - Function *thought* replicating the behavior of a lambda.
  - Configuration system allowing all LLM with class inheritance.
  - *\_\_suggest\_\_* attribute giving advice to improve a prompt. 
- **Fixes**
- **Changes**
- **Optimizations**
- **Internal**

---
