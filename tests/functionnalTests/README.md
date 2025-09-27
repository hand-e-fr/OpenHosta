# Functional Tests

Functional tests are designed to verify that the application behaves as expected from an end-user perspective. They simulate real user scenarios to ensure that all components of the application work together correctly.

It is a good place to start if you want to learn how to use OpenHosta.

## Running Functional Tests

Open .env file and set your LLM API key:

```env
DEFAULT_LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
```

Then, run the following command to execute the functional tests:

```bash
python tests/functionnalTests/test_emulate.py
``` 

## Main functions

**Ask**: This function sends a prompt to the LLM and retrieves the response.

This is provided for convenience. You can use the LLM provider directly.

**Emulate**: This function ask your LLM to emulate the behavior of a the caller function.

This is the main function of OpenHosta. It allows you to create complex behaviors by chaining multiple calls to the LLM without leaving your pythonic context.
- Natural Language Processing (NLP)
- Classification
- Data Extraction
- Decision Making
- ...

**closure**: This function is used to create a closure around a prompt.

This is useful when you want to create a function that can be called multiple times with different parameters. It allows you to define a prompt with placeholders that can be filled in with different values at runtime.
