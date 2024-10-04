# Changelog

All significant changes to this project will be documented in this file.

---
## **v1.2beta-4**

### **Features**

- **TrainingSet**  
  The `TrainingSet` feature is now available! It allows you to manage datasets for `hosta_injected` functions with the following tools:
  - **`.visualize`**: Visualize the dataset (examples and data) for a specific function and get the list of them.
  - **`.add`**: Add new data into `ho_data`.
  - **`.generate`**: Create data by calling an LLM.

- **New Attributes in Predict Functions**  
  The `Predict` function now includes these new attributes:
  - **`.retrain`**: Retrain the model.
  - **`.continue_train`**: Continue training using the previous weights.
  - **`.emulate`**: Run the prediction function in emulation mode with a model.

### **Enhancements**

- `load_examples` has been renamed to `load_training_example` and now supports datasets in JSON, JSONL, and CSV formats for storage in `hosta_cache`.
- The `Predict` function now supports a **verbose** mode for clearer model operations and includes a **get_loss** attribute to specify a .

## **v1.2beta-3**

- **Fixes**
  - `predict` is now CUDA compatible (currently, CUDA(id) cannot be chosen yet).

- **Enhancements**
  - `merge`now merge with 1.1

## **v1.1-rc4** 27/09/24

- **Feature**
  - Added `suggest` function. Works the same as the `__suggest__` attributs but in a function

- **Doc**
  - Many inconsistencies and errors corrected.

- **Internal**
  - Added Github workflows for linting, formating and testing when pushing to dev and main

- **Fixes**
  - `suggest` attribute `diagramm` is now `diagram`
  
## **v1.1-rc3** 26/09/23

- **Fixes**
  - `emulate` now works when emulated function is called inside another one
  - `emulate` works now with `lru_cache` decorator from `functools` module 

- **Internal**
  - Added custom Exception classes for request and frame errors.
  - Added a loop to find the frame in `_extend_scope`
  - Added a Makefile for cleaning and packaging and tests
---

## **v1.1** 13/09/2024

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

## **v1.0** 29/08/2024:

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