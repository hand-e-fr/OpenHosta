# Documentation
___

Documentation for version: **3.0**

Welcome to **OpenHosta** documentation :). Here you'll find all the **explanations** you need to understand the library, as well as **usage examples** and advanced **configuration** methods for the most complex tasks. You'll also find explanations of the source code for those interested in **contributing** to this project. Check the [Google Colab](https://colab.research.google.com/drive/1XKrPrhLlYJD-ULTA8WHzIMqTXkb3iIpb?usp=sharing) **test files** to help you take your first steps in discovering OpenHosta.

For this project, we have adopted a [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a respectful and inclusive environment for all contributors. Please take a moment to read it.

___

## Introduction

### First Step

OpenHosta is a **Python library** designed to facilitate the integration of **LLMs** into the developer's environment, by adding a layer to the Python programming language without distorting it. It is based on the [**PMAC**](PMAC.md) concept, reimagining the **compilation** process in languages. All our functionalities respect the **syntax and paradigm** of this language. 

The choice of LLM is mostly up to you, depending on your configuration level, moreover the vast majority are compatible. By default, OpenAI's **GPT-4.1** is chosen. This has been tested by our team during development and **provides** a satisfaying level of functionality. 

If you do not have access to any remote LLM and do not have an NVIDIA GPU, we recommand that you try **Gemma3:4b** using ollama. Follow the [installation guide](installation.md) to set up ollama then configure `gemma3:4b` instead of `mistrall-small3.2`. It will be a bit slower and less accurate, but it will work even with image input.

If you have a stong GPU (at least 32GB of VRAM), we recommand that you install **Mistral-small3.2**.

Keep in mind that each request will incur **costs** which are different depending on the model and its location. You can find prices on distributor websites. Here are the prices for the OpenAI API: https://openai.com/api/pricing/. You can also look at the power consumption of you CPU/GPU if you use a local model.

Finally, if you like the project and are thinking of contributing, please refer to our [Contribution Guide](CONTRIBUTING.md)

### Why use OpenHosta?

- **Beyond programming**

OpenHosta enables you to create **complex functions**, including those that were previously **impossible**, by defining **semantic** functions in human language. It handles language processing related to **common sense** or other challenging parameters that are typically difficult to implement in native Python. This tool **simplifies** tasks that would otherwise demand considerable time and expertise, thereby broadening the scope of **possibilities** in Python programming.

- **User-Friendly**

You could argue that OpenHosta is a wrapper around LLMs, but it is much more than that. It is much simpler to learn than other toolkit like LangChain or LlamaIndex. With OpenHosta you can directly access your prompts and customize them. This is possible thanks to the very simple idea of the `MetaPrompt` class. It is a jinja2 template that you can edit to change the way OpenHosta interact with the LLM. After each call to the LLM you can print the conversation and the parsing steps to understand what happened.

- **Python Ecosystem**

OpenHosta integrates **fully** into Python syntax. Our main goal is to push programming to a **higher level**. For example, we send *docstrings* and type annotations, commonly used in Python, to the **LLMs** context. We also integrate **advanced methods** such as *lambdas* and the compatibility with *Pydantic* and *typing*. 

- **Reproductibility**

Although LLMs are known to be **stochastic**, OpenHosta provides a way to make your results as **reproducible** as possible. You can set a **seed** for the random number generator of your local ollama installation, which will be used in all calls to the LLM. This allows you to get the same results when you run the same code multiple times, which is essential for **testing** and **debugging**.

- **Open-Source**

We are an Open-Source project. We believe this philosophy contributes to the **sustainability** and **independence** of the artificial intelligence sphere. AI is a great **revolution**, so let's bring it **forward** in the best possible way. We count on your **feedback** and **contributions** to keep OpenHosta evolving.

---

### *Legal Framework*

The use of AI in a production context raises important **legal** issues. It is essential to take these issues into account to ensure the compliance of your **deployment**.

- **Legal Compliance**
For any deployment, it is recommended to verify with an **AI expert** the legal compliance of your use of AI. Indeed, AI is subject to specific **regulations**, particularly in terms of **data protection** and **privacy**. In Europe, the use of AI is governed by the **General Data Protection Regulation** (GDPR) and legislated by the **IA act**. Also, the use of AI in production is subject to specific legal obligations. It is important to take these obligations into account.

- **Security**
The use of AI can also present risks in terms of **cybersecurity**. It is important to take these risks into account to ensure the security of your deployment.
For example **injection attacks** are a major risk when deploying an application using AI. It is important to take measures to protect your application against injection attacks, such as using data validation mechanisms and content filtering.

For more information, please consult the following links:

- [AI Act](https://artificialintelligenceact.eu)
- [GDPR](https://gdpr-info.eu)
- [Prompt Injection Attack](https://www.ibm.com/topics/prompt-injection)

---

Let's **get started**! First here's the **table of contents** to help you navigate through the various sections of the documentation.

## Table of Content

- [Documentation](#documentation)
  - [Introduction](#introduction)
    - [First Step](#first-step)
    - [Why use OpenHosta?](#why-use-openhosta)
    - [*Legal Framework*](#legal-framework)
  - [Table of Content](#table-of-content)
  - [Get Started](#get-started)
    - [Make sure you have installed OpenHosta](#make-sure-you-have-installed-openhosta)
    - [OpenHosta Example](#openhosta-example)
    - [Basic Setup](#basic-setup)
  - [List of supported environnemnt variables](#list-of-supported-environnemnt-variables)
  - [Reasoning models](#reasoning-models)
  - [Changing the MetaPrompt](#changing-the-metaprompt)
  - [`emulate` Function](#emulate-function)
  - [Asynchronous Mode](#asynchronous-mode)
    - [Supported types \& Pydantic](#supported-types--pydantic)
      - [Integration Details](#integration-details)
  - [Closures or Lambda functions](#closures-or-lambda-functions)
  - [`ask` function](#ask-function)
  - [Advanced configuration](#advanced-configuration)
    - [Models](#models)
      - [Inheriting from the OpenAICompatibleModel Class](#inheriting-from-the-openaicompatiblemodel-class)
      - [Custom LLM Call Function](#custom-llm-call-function)
      - [Example Usage](#example-usage)
      - [Show me the prompt !](#show-me-the-prompt-)
  - [References](#references)

---

## Get Started

For each part, you'll find functional examples to illustrate the features. If you have any questions, don't hesitate to visit the “Discussion” tab on GitHub.

### Make sure you have installed OpenHosta

Did you configure your environment variables correctly? If you haven't done so yet, please refer to the [installation guide](installation.md).

If you need to change your .env file, you can find an example in the `tests` folder.

You can reload your credentials from the .env without restarting your interpreter with:

```python
from OpenHosta import reload_dotenv
reload_dotenv()
```

### OpenHosta Example

```python
from OpenHosta import emulate

def translate(text:str, language:str)->str:
    """
    This function translates the text in the “text” parameter into the language specified in the “language” parameter.
    """
    return emulate()

result = translate("Hello World!", "French")
print(result)
```

```python
from OpenHosta import emulate
from dataclasses import dataclass

@dataclass
class Client:
  name:str
  surname:str
  company:str
  email:str
  town:str
  address:str


def extract_client_name(text:str)->Client:
    """
    This function translates the text in the “text” parameter into the language specified in the “language” parameter.
    """
    return emulate()

client1 = extract_client_name("FROM: sebastien@somecorp.com\nTO: shipment@hand-e.fr\nObject: do not send mail support@somecorp.com\n\nto Hello bob, I am Sebastian from Paris, france. Could you send me a sample of your main product? my office address is 3 rue de la république, Lyon 1er")
print(client1)
# Client(name='Sebastian', surname='None', company='somecorp.com', email='sebastien@somecorp.com', town='Lyon', address='3 rue de la république, Lyon 1er')
```

### Basic Setup

This section focuses on the *config* module.

As previously mentioned, a default model is automatically assigned: GPT-4.1. To use it, you first need to enter your API key.

Two methods for that, either you set an environment variable (see the [Installation guide](installation.md)), or you can set it with the following function:

You can also change the default model with:
```python
from OpenHosta import config

config.DefaultModel.base_url = "http://localhost:11434/v1"
config.DefaultModel.model_name = "gpt-oss:20b"
config.DefaultModel.api_key = "not used by ollama local api"
```

If you want to use handle many models, you'll need to create instances of the *OpenAICompatibleModel* class.

```python
from OpenHosta import OpenAICompatibleModel, config

my_model = OpenAICompatibleModel(
    model_name="gpt-4o", 
    base_url="https://api.openai.com/v1/chat/completions",
    api_key="put-your-api-key-here"
)

config.DefaultModel = my_model # set it as the default model for all functions using default pipeline
```

## List of supported environnemnt variables 

```
OPENHOSTA_DEFAULT_MODEL_API_KEY="your_api_key"
OPENHOSTA_DEFAULT_MODEL_BASE_URL="https://api.openai.com/v1" # Optional
OPENHOSTA_DEFAULT_MODEL_NAME="gpt-5"                 # Default to "gpt-4.1" 
OPENHOSTA_DEFAULT_MODEL_TEMPERATURE=0.7              # Optional
OPENHOSTA_DEFAULT_MODEL_TOP_P=0.9                    # Optional
OPENHOSTA_DEFAULT_MODEL_MAX_TOKENS=2048              # Optional
OPENHOSTA_DEFAULT_MODEL_SEED=42                      # Optional. If set with a local LLM your application will be deterministic.
OPENHOSTA_RATE_LIMIT_WAIT_TIME=60                    # When OpenAI API return code 429 (RateLimitError) wait this ammount of seconds before retry. (0 for no retry)
```

## Reasoning models

When you use reasoning models like DeepSeek-R1, OpenHosta is automatically identifying the reasoning part and removes it before casting the output.

```python
from OpenHosta import OpenAICompatibleModel, config

gpt_oss_20b = OpenAICompatibleModel(
        base_url="http://localhost:11434/v1",
        model_name="gpt-oss:20b",
        timeout=180, # More time because the model can take a while to answer due to its reasoning part
        api_key="none"
        )

config.DefaultModel = gpt_oss_20b

def sum_numbers(a:int, b:int)->int:
    """
    This function returns the sum of two numbers.
    """
    return emulate()

result = sum_numbers(12, 30)

from OpenHosta import print_last_prompt

print_last_prompt(sum_numbers)

# Model
# -----------------
# name=gpt-oss:20b
# basse_url=http://localhost:11434/v1


# System prompt:
# -----------------
# You will act as a simulator for functions that cannot be implemented in actual code.

# I'll provide you with function definitions described in Python syntax. 
# These functions will have no body and may even be impossible to implement in real code, 
# so do not attempt to generate the implementation.

# Instead, imagine a realistic or reasonable output that matches the function description.
# I'll ask questions by directly writing out function calls as one would call them in Python.
# Respond with an appropriate return value, without adding any extra comments or explanations.
# If the provided information isn't enough to determine a clear answer, respond simply with "None".
# If assumptions need to be made, ensure they stay realistic, align with the provided description.

# Here's the function definition:

# ```python

# def sum_numbers(a: int, b: int) -> int:
#     """
#     This function returns the sum of two numbers.
#     """

#     ...
#     ...behavior to be simulated...
#     ...

#     return ...appropriate return value...
# ```


# User prompt:
# -----------------

# sum_numbers(a = 12, b = 30)

# Rational:
# -----------------
# The user calls sum_numbers(a=12, b=30). Function returns sum of two numbers, so return 42. No other nuance.

# LLM response:
# -----------------
# 42

```

We see the entire conversation with the LLM. The reasoning part is in the *Rational* section. OpenHosta automatically removes it before casting the output to the expected type (here `int`).

## Changing the MetaPrompt

You can change the MetaPrompt used by OpenHosta's default pipeline to interact with the LLM. This can be useful if you want to customize the behavior of OpenHosta or if you want to use a different prompt for a specific model.


```python
from OpenHosta import config, MetaPrompt

# This is the Meta Prompt used by default for the system part of the conversation
print(config.DefaultPipeline.emulate_meta_prompt)

# This is the Meta Prompt used by default for the user part of the conversation
print(config.DefaultPipeline.user_call_meta_prompt)

# {% if variables_initialization %}# Values of parameters to be used
# {{ variables_initialization }}{% endif %}
# {{ function_name }}({{ function_call_arguments }})

# Change the default MetaPrompt for the user part of the conversation.
# This example was once usefull to prevent qwen models from thinking.
config.DefaultPipeline.user_call_meta_prompt.source += """\n/no_think"""

```

You can also build your own MetaPrompt from scratch.

```python
from OpenHosta import MetaPrompt

# This show how the indentation is removed with dedent. It makes your code more readable.
def my_meta_prompt():
    return MetaPrompt("""
        Explain jinja2 syntax and why using dedent is usefull.
        Try to return a Python code for the function `{{ function_name }}`.
        """)

new_prompt = my_meta_prompt()


print(new_prompt)
# Explain jinja2 syntax and why using dedent is usefull.
# Try to return a Python code for the function `{{ function_name }}`.

print(new_prompt.render(function_name="my_function"))
# Explain jinja2 syntax and why using dedent is usefull.
# Try to return a Python code for the function `my_function`.

# Once you have created your MetaPrompt, you can set it as the default for the user part of the conversation.
config.DefaultPipeline.user_call_meta_prompt = new_prompt
```

Let's see how this new MetaPrompt would work in practice.

```python
def my_function(a:int, b:int)->int:
    """
    This function returns the sum of two numbers.
    """
    return emulate()

result = my_function(12, 30)

print(result)
# The model got confused and returned None.

# You can now investigate what happened by printing the last prompt used.
print_last_prompt(my_function)

# You can also print the pipeline tying steps:
from OpenHosta import print_last_decoding
print_last_decoding(my_function)
```


## `emulate` Function

The *emulate* function is the main feature of OpenHosta. This is the function that allows you to emulate functions with AI, i.e. the instructions will be executed in an LLM and not directly in your computer. Here's how to use it.

Emulate is used inside a function or a class method. What it does is it takes the function's documentation as a “prompt” to emulate it. The way in which you write the function is therefore crucial to ensure that “emulate” works properly.

Here's what you need to know:
  - **The function prototype** is one of the elements sent to LLM. Its different fields must therefore appear clearly. Give a meaningful and precise name to your function. It's also a good idea to annotate your function by specifiing the type of arguments and the type of return. It gives to the LLM the exact format in which it must respond, therefore enhancing it's performance.
  If you're not familliar with the Python annotation system, please check the [typing module documentation](https://docs.python.org/3/library/typing.html)

```python
from typing import List

def example_function(a:int, b:str)->List[str]:
```
  - **The docstring** is the other key element. This is where you describe the behavior of the function. Be precise and concise. Describe the input parameters and the nature of the output, as in a docstring. Feel free to try out lots of things, prompt engineering is not a closed science. :)

```python
from OpenHosta import emulate

def find_name_age(sentence:str, id:dict)->dict:
    """
    This function find in a text the name and the age of a person.

    Args:
        sentence: The text in which to search for information
        id: The dictionary to fill in with information

    Return:
        A dictionary identical to the one passed in parameter, but filled with the information. 
        If the information is not found, fill with the values with “None”.
    """
    return emulate()

ret = find_name_age("the captain's age is one year more than the cabin boy's, who is 22 years old", {"captain": 0, "cabin boy": 0})
print(ret)
# {'captain': 23, 'cabin boy': 22}
```

`emulate` also accepts `force_llm_args` argument: they correspond to the parameter of the LLM provided in the API body.
You can find theses in your model's offcial documentation, but here's a few common:
  - `temperature`
  - `top_p`
  - `max_tokens` 
  - (...)

## Asynchronous Mode

`emulate` can also be used in asynchronous mode. This can be useful if you want to use OpenHosta in a web application or a bot. It also simplifies the use of multiple calls to the LLM in parallel with `asyncio`.

To use `emulate` in asynchronous mode, you need to use the `emulate` function from `OpenHosta.asynchrone` module with the `await` keyword. 
It works the same way as `emulate`, but it returns an `awaitable` object. If you need to mix synchronous and asynchronous code, you can use the `emulate` and `emulate_async` functions together.

```python
import asyncio
from OpenHosta.asynchrone import emulate

## You can also import it like this if you need both synchronous and asynchronous versions in the same file
# from OpenHosta import emulate, emulate_async

async def capitalize_cities(sentence:str)->str:
    """
    This function capitalize the first letter of all city names in a sentence.
    """
    return await emulate()

# From native python interpreter you shall use asyncio.run
try:
  sentence = asyncio.run(capitalize_cities("je suis allé à londres et los angeles en juin"))
except:
  print("You are in a notebook or a python interpreter that does not support asyncio.run")

# From Google colab or jupyter
try:
  sentence = await capitalize_cities("je suis allé à londres et los angeles en juin")
except:
  print("You are in python interpreter that does not support async")


print(sentence)
# 'je suis allé à Londres et Los Angeles en juin'
```

Functions that are available in asynchronous mode:

  - `ask`
  - `emulate`
  - `closure`
  - `test`

### Supported types & Pydantic

`emulate` support for the **typing** module: You can now use specific return types from the typing module, including [`List`, `Dict`, `Tuple`, `Set`, `FrozenSet`, `Deque`, `Iterable`, `Sequence`, `Mapping`, `Union`, `Optional`, `Literal`].

> **Note:**
> Annotate your function's return value as `Optional` tends to make the LLM respond with `None` in case of an inconsistent input. This can become useful when using `OpenHosta` in larger and more complex programm. 

```python
from OpenHosta import emulate
from typing import Dict, Tuple, List

def analyze_text(text: str) -> Dict[str, List[Tuple[int, str]]]:
    """Analyze text to map each word to a list of tuples containing word length and word."""
    return emulate()

# Example usage
analysis = analyze_text("Hello, World!")

print(analysis)
# {'Hello': [(5, 'Hello')], 'World': [(5, 'World')]}

print(type(analysis))
# <class 'dict'>
```

It also includes a verification output that checks and converts the output to the specified type if necessary. Supported types include **Pydantic** models, all types from the **typing** module mentioned above, as well as built-in types such as `dict`, `int`, `float`, `str`, `list`, `set`, `frozenset`, `tuple`, and `bool`.
The `complex` type is not supported. If you need to use complex numbers, please pass them as a `tuple` and manually convert them after processing.

OpenHosta integrates with Pydantic, a library for data validation and settings management using Python type annotations. This integration allows you to use Pydantic models directly within `emulate`, ensuring data consistency and validation.

Pydantic provides a way to define data models using Python types. It automatically validates and converts input data to match these types, ensuring that your application processes data safely and accurately.

For more information, please read the official [Pydantic documentation](https://docs.pydantic.dev/latest/api/base_model/).

#### Integration Details

OpenHosta supports Pydantic typing by accepting Pydantic models as input of an emulated function. This offers:

- **Type Safety:** Ensures data integrity through Python's type hints.
- **Automatic Validation:** Validates input data against Pydantic models, reducing manual checks.
- **Data Parsing:** Converts input data to specified types, simplifying data handling.

The Pydantic model will be automatically processed by our tools and the LLM to guarantee a stable output.
The Pydantic model cannot be defined inside a function, as this will produce an error.
Let's take the same example, but using this feature:

```python
from pydantic import BaseModel
from OpenHosta import emulate

class Person(BaseModel):
    name: str
    age: int

def find_first_name(sentence:str)->Person:
    """
    This function find in a text the name and the age of a person.

    Args:
        sentence: The text in which to search for information

    Return:
        A Pydantic model, but filled with the information. 
        If the information is not found, fill with the values with “None”.
    """
    return emulate()

find_first_name("the captain's age is one year more than the first officer's age. The first officer is 30 years old")
# Person(name='first officer', age=30)
```

## Closures or Lambda functions

**Lambda** functions in Python provide a way to create small, anonymous functions. These are defined using the lambda keyword and can have any number of input parameters but only a single expression. We implemented a similar feature in OpenHosta named `closure`.

**Key Characteristics**
  - **Anonymous**: Lambda functions do not require a name, making them suitable for short-lived operations.
  - **Concise Syntax**: Defined in a single line using the syntax lambda arguments: expression.
  - **Single Expression**: Can only contain a single expression, which is evaluated and returned.
  
For more information, please check https://python-reference.readthedocs.io/en/latest/docs/operators/lambda.html

In an aim to integrate with Python syntax, we've developed the `closure` function. It replicates the same behavior as lambda.

Here's how it works:

```python
from OpenHosta import closure

x = closure("Is it a masculine name")
print(x("John"))  # True

result = closure("Multiply by two")(2)
print(result)   # 4
```

In the example above, we can see two distinct ways of using `closure`. In the first example, you can store a lambda function in a variable and then use it. You can also call it directly by enclosing the arguments behind it in brackets. `closure` accepts multiple arguments and all types native to python. However, the content of the first bracket is always a string.

The `closure` function has an initial pre-compilation stage where it predicts the type of the return value by making an initial call to an LLM. Execution time can therefore be increased the first time using the function, then the type is stored and reused for the next execution.

```python
from OpenHosta import closure

x = closure("Adds all integers")
ret = x(2 ,3 ,6) # 11
```

## `ask` function

The function `ask` is a sort of a *side* function In OpenHosta. Its only use is to make a simple LLM call without the OpenHosta's meta-prompt. It simplies the process af an API call and the parsing of the response. It is useful for quick tests or interactively from a notebook.

```python
from OpenHosta import ask

print(ask("Do you know about scikit-learn?"))

# Yes, I know about **scikit-learn**!

# **Scikit-learn** (often imported as `sklearn`) is one of the most popular open-source Python libraries for **machine learning** and **data analysis**. It provides a wide range of simple and efficient tools for data mining and data modeling, built on top of **NumPy**, **SciPy**, and **matplotlib**.

# ### Common Features

# - **Supervised learning** (classification and regression)
# - **Unsupervised learning** (clustering, dimensionality reduction)
# - **Model selection** (cross-validation, grid search)
# - **Data preprocessing** (scaling, encoding, imputation)
# - Built-in datasets
# - **Pipelines** for automating workflows
# [...]
```

This is equivalent to the following OpenAI API call:

```python
import openai

openai.api_key = "your-api-key-here"

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Do you know about scikit-learn?"}
]

response = openai.ChatCompletion.create(
    model="gpt-4.1",
    messages=messages
)

print(response['choices'][0]['message']['content'])
```

You can leverage `MetaPrompt` to customize the system prompt:

```python
from OpenHosta import ask, MetaPrompt
system_prompt = MetaPrompt("You are a helpful assistant specialized in {domain}.")
print(ask("What is overfitting?", system=system_prompt.render(domain="machine learning")))
``` 

## Advanced configuration

### Models

This section explains how to customize the program to make its own LLM call and response handling functions. This can be useful if you need a specific functionality that is not provided by the standard library, or to enable compatibility with a specific LLM. 

#### Inheriting from the OpenAICompatibleModel Class

The first step is to inherit from the OpenAICompatibleModel class to create your own configuration class. The OpenAICompatibleModel class provides a base for the library's configuration, including connection settings to the LLM and response handling functions.

```python
from OpenHosta import OpenAICompatibleModel

class MyModel(OpenAICompatibleModel):
    # Your code here
```

In the example above, we have created a new class `MyModel` that inherits from the OpenAICompatibleModel class. This means that `MyModel` has access to all the methods and attributes of the OpenAICompatibleModel class. You can now add your own functions to this class to customize the OpenHosta's configuration.
You can also override an existing function to modify its behavior. It is important to keep input/output components identical in order to avoid errors when interacting with calling functions.

#### Custom LLM Call Function

To create your own LLM call function, you need to override the `api_call` method of the OpenAICompatibleModel class. This method is called every time the library needs to communicate with the LLM.

```python
from typing import Dict, List
from OpenHosta import OpenAICompatibleModel

class MyModel(OpenAICompatibleModel):
    def api_call(
        self,
        messages: list[dict[str, str]],
        llm_args:dict = {}
    ) -> Dict:
        # Your code here
        # Call the LLM and return the response
        return response
```

In the example above, we have overridden the "api_call" method of the OpenAICompatibleModel class to create our own LLM call function.
The "api_call" method takes four arguments:

- **message**: The parsed message sent to the LLM.
- **llm_args**: All the options given by the LLM's distributor. (ex. max_token, temperature, top_p...)

The "api_call" method returns a response object that contains the LLM's response to the user prompt.

#### Example Usage

You can now create an instance of the class you've just created and use it in all OpenHosta's features.

With this method, you can now make OpenHosta compatible with a large number of API.

**Here's an example of of a custom OpenAICompatibleModel class for Llama models:**

```python
from typing import Dict
from OpenHosta import emulate, OpenAICompatibleModel, OneTurnConversationPipeline
import requests

class LlamaModel(OpenAICompatibleModel):
            
    def api_call(
        self,
        messages: list[dict[str, str]],
        llm_args:dict = {  "stream": False}
    ) -> Dict:
        l_body = {
            "model": self.model_name,
            "prompt": "\n".join([str(x) for x in messages]),
            "stream": False
        }
        headers = {
            "Content-Type": "application/json"
        }

        all_api_parameters = self.api_parameters | llm_args
        for key, value in all_api_parameters.items():
            if key == "force_json_output" and value:
                l_body["response_format"] = {"type": "json_object"}
            else:
                l_body[key] = value
                
        try:
            full_url = f"{self.base_url}{self.chat_completion_url}"
            response = requests.post(full_url, headers=headers, json=l_body, timeout=self.timeout)

            if response.status_code != 200:
                response_text = response.text
                raise Exception(
                    f"[OpenAICompatibleModel.api_call] API call was unsuccessful.\n"
                    f"Status code: {response.status_code }:\n{response_text}"
                )
            self._nb_requests += 1
            return response.json()
        except Exception as e:
            raise Exception(f"[OpenAICompatibleModel.api_call] Request failed:\n{e}\n\n")

    def get_response_content(self, response_dict: Dict) -> str:
        json_string = response_dict["response"]
        return json_string
        

mymodel = LlamaModel(
    model_name="gemma3:4b",
    base_url="http://localhost:11434",
    chat_completion_url="/api/generate",
    api_key="..."
)

def capitalize(sentence:str)->str:
    """
    This function capitalize a sentence in parameter.
    """
    return emulate(pipeline=OneTurnConversationPipeline(model_list=[mymodel]))


print(capitalize("hello world!"))
# Hello world!
```

**Another example to work with Ollama:**

```python
from OpenHosta import OpenAICompatibleModel, ask, config

ollama_local_model=OpenAICompatibleModel(
    model_name="gemma3:4b",
    base_url="http://localhost:11434/v1",
    api_key="none"
)
config.DefaultModel = ollama_local_model

ask("hello")
```

**Now with Microsoft Azure:**

```python
from OpenHosta import config, ask, OpenAICompatibleModel

azure_redentials={
    'Client_id': "some specific guid",
    'Client_secret': "some specific secret",
}

azure_model = OpenAICompatibleModel(
    base_url="https://YOUR_RESOURCE_NAME.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT_NAME", 
    chat_completion_url="/chat/completions?api-version=2023-07-01-preview",
    model_name="gpt-4o",
    additionnal_headers=azure_redentials,
    api_key="unused key"
    )

config.DefaultModel = azure_model

ask("hello")
```

#### Show me the prompt !

To see te full filled prompt send to the LLM and its response, you can also use the `print_last_prompt` and `print_last_response` function:

```python
from OpenHosta import emulate, print_last_prompt, print_last_response

def multiply(a:int, b:int)->int:
    """
    This function multiplies two integers in parameter.
    """
    return emulate()

multiply(5, 6)
print_last_prompt(multiply)
print_last_response(multiply)
```


---

## References

- **LLM**: https://en.wikipedia.org/wiki/Large_language_model
- **GPT-4o**: https://en.wikipedia.org/wiki/GPT-4o
- **AI**: https://en.wikipedia.org/wiki/Artificial_intelligence
- **NLP**: https://en.wikipedia.org/wiki/Natural_language_processing
- **Zero-Shot Prompting**: https://www.promptingguide.ai/techniques/zeroshot
- **Few-Shot Prompting**: https://www.promptingguide.ai/techniques/fewshot
- **Chain-of-Thought**: https://www.promptingguide.ai/techniques/cot

---

We hope you find all the information you need. We are proud to present the new version of this project. 
The OpenHosta team. :)

---

