# Documentation
___

Documentation for version: **2.0.0**

Welcome to **OpenHosta** documentation :). Here you'll find all the **explanations** you need to understand the library, as well as **usage examples** and advanced **configuration** methods for the most complex tasks. You'll also find explanations of the source code for those interested in **contributing** to this project. Check the [Google Colab](https://colab.research.google.com/drive/1XKrPrhLlYJD-ULTA8WHzIMqTXkb3iIpb?usp=sharing) **test files** to help you take your first steps in discovering OpenHosta.

For this project, we have adopted a [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a respectful and inclusive environment for all contributors. Please take a moment to read it.

___

## Introduction

### First Step

OpenHosta is a **Python library** designed to facilitate the integration of **LLMs** into the developer's environment, by adding a layer to the Python programming language without distorting it. It is based on the [**PMAC**](PMAC.md) concept, reimagining the **compilation** process in languages. All our functionalities respect the **syntax and paradigm** of this language. 

The choice of LLM is mostly up to you, depending on your configuration level, moreover the vast majority are compatible. By default, OpenAI's **GPT-4o** is chosen. This has been tested by our team during development and **provides** a satisfaying level of functionality. 

Whatever your configuration, make sure you own a **working API key** before proceeding. Keep in mind that each request will incur **costs** which are different depending on the model. You can find prices on distributor websites. Here are the prices for the OpenAI API: https://openai.com/api/pricing/

We've already mentioned a few concepts about **AI** or **computer science**. If some of them are **unclear** to you, please have a look at the *“references”* section, where a series of explanatory links or definitions will be listed to **help** you understand.

Finally, if you like the project and are thinking of contributing, please refer to our [Contribution Guide](CONTRIBUTING.md)

### Why use OpenHosta?

- **Beyond programming**

OpenHosta enables you to create **complex functions**, including those that were previously **impossible**, by accommodating certain **ambiguities** in human language. It handles language processing related to **common sens** or other challenging parameters that are typically difficult to implement in Python. This tool **simplifies** tasks that would otherwise demand considerable time and expertise, thereby broadening the scope of **possibilities** in Python programming.

- **Python Ecosystem**

OpenHosta integrates **fully** into Python syntax. Our main goal is to push programming to a **higher level**. For example, we send *docstrings*, commonly used in Python, to the **LLMs** context. We also integrate **advanced methods** such as *lambdas* and the compatibility with *Pydantic* and *typing*. 

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
    - [OpenHosta Example](#openhosta-example)
    - [Install OpenHosta](#install-openhosta)
    - [Librairie Import](#librairie-import)
    - [Basic Setup](#basic-setup)
  - [`emulate` Function](#emulate-function)
    - [Supported types \& Pydantic](#supported-types--pydantic)
      - [Integration Details](#integration-details)
    - [Body Functions](#body-functions)
      - [`Example`](#example)
      - [`Thought`](#thought)
  - [`thinkof` Function](#thinkof-function)
  - [`ask` function](#ask-function)
  - [Advanced configuration](#advanced-configuration)
    - [Models](#models)
      - [Inheriting from the Model Class](#inheriting-from-the-model-class)
      - [Custom LLM Call Function](#custom-llm-call-function)
      - [Custom Response Handling Function](#custom-response-handling-function)
      - [Create a new instance](#create-a-new-instance)
    - [Prompts](#prompts)
      - [Edit the prompt](#edit-the-prompt)
      - [Show me the prompt !](#show-me-the-prompt-)
  - [References](#references)

---

## Get Started

For each part, you'll find functional examples to illustrate the features. If you have any questions, don't hesitate to visit the “Discussion” tab on GitHub.

### OpenHosta Example

```python
from OpenHosta import emulate, config

def translate(text:str, language:str)->str:
    """
    This function translates the text in the “text” parameter into the language specified in the “language” parameter.
    """
    return emulate()

result = translate("Hello World!", "French")
print(result)
```

### Install OpenHosta

The installations process is described step-by-step in the [installation guide](installation.md).

Once you've installed the OpenHosta library, you're ready to get started. We'll import the library and then look at the basic configurations.

### Librairie Import

```python
from OpenHosta import *
```

We recommend this import method, as it gives you all the important and stable features:
  - All the tools to emulate Python function (`emulate` and all it's attached functions)
  - All the tools to create specialized model (`predict` and all it's attached functions)
  - All the others features useful in `OpenHosta` (`ask`, `thinkof`, tools for data generation...)
  - Configuration tools

But you can also import modules one by one.

```python
from OpenHosta import emulate, config
```

### Basic Setup

This section focuses on the *config* module.

As previously mentioned, a default model is automatically assigned: GPT-4o. To use it, you first need to enter your API key.

Two methods for that, either you set an environment variable (see the [Installation guide](installation.md)), or you can set it with the following function:

```python
config.set_default_apiKey("put-your-api-key-here")
```

Once you've done that, all OpenHosta's features are ready to use.

If you want to use another model, you'll need to create an instance of the *Model* class.

```python
my_model = config.Model(
    model="gpt-4o", 
    base_url="https://api.openai.com/v1/chat/completions",
    api_key="put-your-api-key-here"
)
```

Note that some features like `thinkof` or `LLMSyntheticDataGenerator` specifically use the default model. So if you want to change it, use this:

```python
config.set_default_model(my_model)
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
  - **The doctring** is the other key element. This is where you describe the behavior of the function. Be precise and concise. Describe the input parameters and the nature of the output, as in a docstring. Feel free to try out lots of things, prompt engineering is not a closed science. :)

```python
my_model = config.Model(
    model="gpt-4o", 
    base_url="https://api.openai.com/v1/chat/completions",
    api_key="put-your-api-key-here"
)

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
    return emulate(model=my_model)
```

Note that, as seen above, you can pass a previously configured model as an emulate parameter.

Be careful, you can put regular instructions in your function and they will be executed. However, `emulate` can retrieves all the variables local to the functions and gives them to the LLM as a context with the `use_locals_as_ctx` parameter (set at `True`). If your emulated function is a class method, `emulate` can retrieves all the attributes of this class to also give them as context with the `use_self_as_ctx` parameter.

Another parameter of `emulate` is `post_callback`. It take a callable as input and allows you to execute it to the output of the LLM. This can be useful for logging, error handling or formatting multiple emulated function's output with a single function. The callable passed take one argument which is the output of the LLM and must return another value. If the output of the LLM won't change during the execution of your callback, just return the value given in argument. 

`emulate` also accepts other unspecified arguments: they correspond to the parameter of the LLM.
You can find theses in your model's offcial documentation, but here's a few common:
  - `temperature`
  - `top_p`
  - `max_tokens` 
  - (...)

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
print(type(analysis))
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
```

### Body Functions

In addition to the docstring-as-prompt, you can enhance your prompting with specialized functions. This way you can try different techniques like Zero/Few-shot prompting or Chain-of-Thought. If you're not familliar with theses concept, please check the [Reference](#references) section.

#### `Example`

The first of the body function is `example`. It allow you to give example to LLM.

```python
from OpenHosta import emulate, example

def is_positive(sentence:str)->bool:
    """
    This function return True if the sentence in parameter is positive, False otherwise. 
    """
    example(sentence="Marc got a good mark in his exam.", hosta_out=True)
    example(sentence="The weather is awful today !", hosta_out=False)
    return emulate()

print(is_positive("I can do it !")) # True

# It will be write as follow in the final prompt:
#######
# Here are some examples of expected input and output:
#[{'in_': {'sentence': 'Marc got a good mark in his exam.'}, 'out': True}, {'in_': {'sentence': 'The weather is awful today !'}, 'out': False}]
```

As shown above, `example` takes two types of argument. There are input parameters which must be named (kwargs) and exactly be the same number and type as in the function's definition. Finally, there's the “hosta_out” parameter. This corresponds to the expected LLM output.

Giving inconsistent examples can severely impact LLM performance. But it can be a very good tool if it's used properly. 

#### `Thought`

The second body function is `thought`. It allows you to create chain of thought inside your prompt to enhance it's performance for more complex tasks.

```python
from OpenHosta import emulate, thought
from typing import List, Optional

def car_advice(query:str, car_available:List[str])->Optional[str]:
    """
    This function gives the best advice for the query in parameter. It must return the best car in the list "car_available" fitting the user's needs.
    If no car fit the user's needs, this function returns None.
    """
    thought("identify the context and the need of the user")
    thought("Look at the car available to find a car matching his needs")
    thought("Return the name of the most relevant car, if no car is matching return None")
    return emulate()

car_list = [
    "Lamborghini Aventador LP700-4",
    "Volkswagen Coccinelle type 1",
    "Ford Mustang 2024"
]

print(car_advice("I lives in the center of a big city with a lot of traffic, what do you recommend ?", car_list))
# Volkswagen Coccinelle type 1
print(car_advice("I would two buy a new car, but I would like an electric because I don't want to ruin my planet.", car_list))
# None

# It will be write as follow in the final prompt:
#####
# To solve the request, you have to follow theses intermediate steps. Give only the final result, don't give the result of theses intermediate steps:
# [{'task': 'identify the context and the need of the user'}, {'task': 'Look at the car available to find a car matching his needs'}, {'task': 'Return the most relevant car, if no car is matching return None'}, {'task': 'identify the context and the need of the user'}, {'task': 'Look at the car available to find a car matching his needs'}, {'task': 'Return the most relevant car, if no car is matching return None'}]
```

## `thinkof` Function

**Lambda** functions in Python provide a way to create small, anonymous functions. These are defined using the lambda keyword and can have any number of input parameters but only a single expression.

**Key Characteristics**
  - **Anonymous**: Lambda functions do not require a name, making them suitable for short-lived operations.
  - **Concise Syntax**: Defined in a single line using the syntax lambda arguments: expression.
  - **Single Expression**: Can only contain a single expression, which is evaluated and returned.
  
For more information, please check https://python-reference.readthedocs.io/en/latest/docs/operators/lambda.html

In an aim to integrate with Python syntax, we've developed the `thinkof` function. It replicates the same behavior as lambda.

Here's how it works:

```python
from OpenHosta import thinkof

x = thinkof("Is it a masculine name")
print(x("John"))  # True

result = thinkof("Multiply by two")(2)
print(result)   # 4
```

In the example above, we can see two distinct ways of using `thinkof`. In the first example, you can store a lambda function in a variable and then use it. You can also call it directly by enclosing the arguments behind it in brackets. `thinkof` accepts multiple arguments and all types native to python. However, the content of the first bracket is always a string.

The `thinkof` function has an initial pre-compilation stage where it predicts the type of the return value by making an initial call to an LLM. Execution time can therefore be increased the first time using the function, then the type is stored and reused for the next execution.
You can retrieve the predicted return type with the `_return_type` attribute attached to the object:

```python
from OpenHosta import thinkof

x = thinkof("Adds all integers")
ret = x(2 ,3 ,6)
print(x._return_type) # int
```

**Note** : ***this feature uses the default model.***

## `ask` function

The function `ask` is a sort of a *side* function In OpenHosta. Its only use is to make a simple LLM call without the OpenHosta's meta-prompt. It simplies the process af an API call.

```python
from OpenHosta import ask, Model

print(
    ask(
        system="You're a helpful assistant."
        user="Write me a cool story."
        max_tokens=200
    )
)
```

The "traditional" would be like this:

```python
import openai

openai.api_key = "your-api-key-here"

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Write me a cool story."}
]

response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=messages
)

print(response['choices'][0]['message']['content'])
```

As seen above takes 2 or more argument. The two first arguments are mandatory. `system` correspond to the system prompt to the LLM, same as the `user` parameter. You can also set the `model` parameter to a custom Model instance. It also handle all LLM parmaters (`max_tokens`, `n`, `top_p`...).

**Note** : ***this feature uses the default model.***

## Advanced configuration

### Models

This section explains how to customize the program to make its own LLM call and response handling functions. This can be useful if you need a specific functionality that is not provided by the standard library, or to enable compatibility with a specific LLM. 

#### Inheriting from the Model Class

The first step is to inherit from the Model class to create your own configuration class. The Model class provides a base for the library's configuration, including connection settings to the LLM and response handling functions.

```python
from OpenHosta import Model

class MyModel(Model):
    # Your code here
```

In the example above, we have created a new class `MyModel` that inherits from the Model class. This means that `MyModel` has access to all the methods and attributes of the Model class. You can now add your own functions to this class to customize the OpenHosta's configuration.
You can also override an existing function to modify its behavior. It is important to keep input/output components identical in order to avoid errors when interacting with calling functions.

#### Custom LLM Call Function

To create your own LLM call function, you need to override the `api_call` method of the Model class. This method is called every time the library needs to communicate with the LLM.

```python
from OpenHosta import Model

class MyModel(Model):
    def api_call(self, sys_prompt, user_prompt, creativity, diversity):
        # Your code here
        # Call the LLM and return the response
        return response
```

In the example above, we have overridden the "api_call" method of the Model class to create our own LLM call function.
The "api_call" method takes four arguments:

- **sys_prompt**: a string that specifies the system prompt to be sent to the LLM. It's all the basic instructions to give context to the LLM. It is not function-dependent, but feature-dependent.. System prompts provided by OpenHosta are present in the “prompt.json” file.
- **user_prompt**: a string that specifies the user prompt to be sent to the LLM. It contains all the information relating to the emulated function. They are placed side by side, with sentences to separate each piece of information. This section is therefore unique for each case. 
- **creativity**: a float that specifies the creativity level of the LLM's response.
- **diversity**: a float that specifies the diversity level of the LLM's response.

The "api_call" method returns a response object that contains the LLM's response to the user prompt.

#### Custom Response Handling Function

To create your own response handling function, you need to override the "request_handler" method of the Model class. This method is called every time the library receives a response from the LLM.

```python
from OpenHosta import Model

class MyModel(Model):
    def request_handler(self, response, return_type, return_caller):
        # Your code here
        # Process the LLM response and return the result
        return result
```

In the example above, we have overridden the `request_handler` method of the Model class to create our own response handling function. 
The "request_handler" method takes three arguments:

- **response**: the response object returned by the LLM.
- **return_caller**: the type of the return value. For an “int” return type, it would be as follows
  ```<class :'int'>```
- **return_type**: a JSON describing the type of the return value. This JSON is mainly used for more complex return types such as Pydantic models or classes. For an “int” return type, the JSON would be as follows:
  ```{'properties': {'return_hosta_type': {'title': 'Return Hosta Type', 'type': 'integer'}}, 'required': ['return_hosta_type'], 'title': 'Hosta_return_shema', 'type': 'object'}```

The "request_handler" method returns the processed return value. This is the value returned by the emulated function.

#### Create a new instance

You can now create an instance of the class you've just created and use it in all OpenHosta's features.

```python
from OpenHosta import config, Model, emulate, thought

class MyModel(Model):

    def api_call(self, sys_prompt, user_prompt, creativity, diversity):
        # Your code here
        # Call the LLM and return the response
        return response

    def request_handler(self, response, return_type, return_caller):
        # Your code here
        # Process the LLM response and return the result
        return l_ret

new_model = MyModel(
    model="model-name"
    base_url="base-url"
    api_key="put-your-api-key-here"
)

def capitalize(a:str)->str:
    """
    This function capitalize a sentence in parameter.
    """
    return emulate(model=new_model)

print(capitalize("hello world!"))

config.set_default_model(new_model)

x = thought("Translate in german")
ret = x("Hello World")
print(ret)
```

### Prompts

#### Edit the prompt

`emulate` works by putting the emulated function's parsed data in a meta-prompt designed to give the best performance and ensure a constant ouptput format. But you can different parts of this meta-prompt. Here's how you do it.

You first need to import `EMULATE_PROMPT`

```python
from OpenHosta import EMULATE_PROMPT
```

This is an instance of a class conatining attributes. These attributes are all the separated parts (named "shards") of the prompt, that are then combined to build the final prompt. You'll only need to change theses attributes to change automatically the prompt.

Here's all the shards:
- **CTX_MAIN**: The main context gived to the LLM.
- **CTX_SEP1**: The separator between the context and the example.
- **CTX_EXAMPLE**: The examples decribing the overall functioning of OpenHosta.
- **CTX_SEP2**: The separator between the context and emulated function's infos. 
- **PRE_DEF**: The sentence introducing the function's definition.
- **PRE_TYPE**: The sentence introducing the function's annotations.
- **PRE_SCHEMA**: The sentence introducing the function's return type's schema.
- **PRE_LOCALS**: The sentence introducing the function's local variables (Optional).
- **PRE_SELF**: The sentence introducing the function's local attributes (Optional).
- **PRE_EXAMPLE**: The sentence introducing the examples given by the user (Optional). 
- **PRE_COT**: The sentence introducing the Chain-of-Thought (Optional).
- **USER_SEP**: The separator between the system prompt and the user prompt.

You can find all the separated values by visiting the [meta_prompt.py](../src/OpenHosta/utils/meta_prompt.py) file.

To see te full filled prompt send to the LLM, you can also use the `print_last_prompt` function:

```python
from OpenHosta import emulate, print_last_prompt

def multiply(a:int, b:int)->int:
    """
    This function multiplies two integers in parameter.
    """
    return emulate()

multiply(5, 6)
print_last_prompt(multiply)
```

#### Show me the prompt !

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

We hope you find all the information you need. We are proud to present the first version of this project. 
The OpenHosta team. :)

---

