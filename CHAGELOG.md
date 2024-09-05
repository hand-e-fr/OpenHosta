# Changelog

All significant changes to this project will be documented in this file.

---

## **v1.1**

- **Fixes**
  - the `emulate` function is now decorator-resistant.
  - The function `config.set_default_model` works now w/ `config.set_default_apiKey`
  - `thought` function now accept multiple arguments
  - `suggest` and `analytics` call now th LLM with `Model` class (`_ai_call`)
  
- **Enhancement**
  - the `thought` function guess automatically his return type with LLM
  - `suggest` return now his data returned by LLM in a dict

- **Doc**
  - Documentation now integrates Google Cobal link

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