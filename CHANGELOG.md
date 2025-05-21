# Changelog

All significant changes to this project will be documented in this file.

---
## **v2.2.2**
- **Fixes**
  - #216 allow sync functions in google colab 

## **v2.2.0**
- **Features**
  - #193 Allow model thinking before answering (DeepSeek R1 compatible) 
  - #197 Support for asyncawait
  - #182 Fix based hyperparameters in predict

- **Internal**
  - stub missing functions when pydantic or predict are not installed
  - #202 add regression tests
  - #32 The emulate prompt could be created dynamically depending on the context. (possibility tree) 

- **Fixes**
  - #195 fix Bug with pydantic import
  - #199 improve pydantic return type support for List[Model] and Dict[..., Model]

## **v2.1.5**
- **Fixes**
  - Allow basic auth for models behind API

- **Doc**
  - List files with versions to be modified at delivery 
  - Update Google colab local llm and agent documentation

## **v2.1.4**
- **Fixes**
  - CUDA compatibility

- **Internal**
  - Added a GitHub Action to push automatically on PyPI on a release

- **Doc**
  - Added `delivery method` to the contributing file

## **v2.1.3**
- **Features**
  - Added `additionnal_headers` in `OpenAICompatibleModel` to add specific values in the header of the request send to the API.
  - `ask` can now be used without specify the `user` parameter name.

- **Fixes**
  - Fixed the bug with the f-string in python 3.10 or below.
  - Removed `simple_api_call`.
  - `Hosta` now support a nested pydantic type like `List[PydanticType]`.

- **Doc**
  - Added two example to work with Microsoft Azure and Ollama.
  - Added documentation for the `emulate` functions.
  - Remplace all links in the `README` by absolute link 

## **v2.1.2**
- **Doc**
  - Fix the example for the custom OpenAICompatibleModel class with a Llama OpenAICompatibleModel

- **Fixes**
  - Remove the PIL dependency

## **v2.1.1**
- **Enhancement**
  - Changed examples syntax in the system prompt for better performances.

- **Doc**
  - Added an example for a custom OpenAICompatibleModel class with an Llama model.  

## **v2.0-beta2**
- **Added**
  - Introduced `BaseEncoder` as an Abstract Base Class (ABC) for all specific encoders, providing a standardized interface.
  - Added `BoolEncoder` to handle encoding of boolean values.
  - Introduced `PredictConfig` data class to encapsulate parameters for the `predict` function.
  - Initial implementation of the `HostaCache` class in `core/cache.py` with generic type support.
  - Initial implementation of the `ModelCachedData` and `HostaModelCache` classes in `predict/cache.py`.
- **Changed**
  - Refactored `IntEncoder` and `FloatEncoder` to inherit from `BaseEncoder` and implement the encode method.
  - Updated `HostaEncoder` to use a dictionary (`self.encoders`) for mapping data types to their corresponding encoders. This allows for easier extension and maintenance.
  - Improved type handling in `HostaEncoder.encode` method for better extensibility and readability.
  - Refactored `predict` function to accept a single `PredictConfig` object instead of multiple parameters. This change improves readability and maintainability of the function.
- **Fixed**
  - Enhanced exception handling in `FloatEncoder` to provide more informative error messages.
  - Removed unnecessary constructors from encoder classes, streamlining the code.

## **v2.0-beta1**

- **Features**
  - Added `max_tokens` args for emulate
  - Added `use_locals/self_as_ctx` args for emulate for clarity and modularity
  - `thought` is now used to add chain of thoughts in a emulated function
  - `PromptManager` is now available for users to change all meta-prompt.

- **Changes**
  - `thought` function become `thinkof`
  - `suggest` is removed
  - `creativity` become `temperature` and `diversity` become `top_p`
  - There's no more `hostacache` for emulated functions

## **OpenHosta v1.2.1 - 10/14/24**

- **Fixes**
  - OpenHosta now can't be used with Python 3.13 due to the incompatibility with pytorch

## **v1.2.0** - 10/14/2024

- **New Features**

  - **`predict` Function**  
    The `predict` function is now available, allowing you to create internal models—currently supporting linear regression—based on user-provided training data. This simplifies model generation without relying on external APIs. Key functionalities include:
    - **`.retrain`**: Retrain models with specified parameters.
    - **`.continue_train`**: Continue training with existing model weights.
    - **`.emulate`**: Run predictions through an LLM or create a model directly using internal linear regression based on training data.

  - **TrainingSet Management**  
    Manage training datasets effortlessly with new tools:
    - **`.visualize`**: Inspect current data visually.
    - **`.add`**: Add new examples.

- **Enhancements**

  - **Expanded Dataset Support**:  
    `load_training_example` (previously `load_examples`) supports JSON, JSONL, and CSV formats for easier integration.

  - **Verbose Mode in `predict`**:  
    Track detailed model training and define target losses with `get_loss`.

---
## **v1.1.1** 10/07/24

- **Features**
  - Added `_last_request` attributs to the `OpenAICompatibleModel` object

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
  - `suggest` and `analytics` call now th LLM with `OpenAICompatibleModel` class (`ai_call`)
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
