# Documentation
___

Documentation for version: **3.0**

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
    - [Basic Setup](#basic-setup)
  - [Reasoning models](#reasoning-models)
  - [`emulate` Function](#emulate-function)
  - [Asynchronous Mode](#asynchronous-mode)
    - [Supported types \& Pydantic](#supported-types--pydantic)
      - [Integration Details](#integration-details)
    - [Body Functions](#body-functions)
      - [`Example`](#example)
      - [`Thought`](#thought)
  - [`predict` Function](#predict-function)
    - [Parameters](#parameters)
  - [`PredictConfig` class](#predictconfig-class)
    - [Features](#features)
      - [**Path Management**](#path-management)
      - [**Architecture Configuration**](#architecture-configuration)
      - [**Training Configuration**](#training-configuration)
      - [**Dataset Management**](#dataset-management)
    - [Example Usage](#example-usage)
  - [`thinkof` Function](#thinkof-function)
  - [`ask` function](#ask-function)
  - [`generate_data` function](#generate_data-function)
    - [Parameters](#parameters-1)
    - [Returns](#returns)
    - [Raises](#raises)
    - [Example](#example-1)
    - [How It Works](#how-it-works)
  - [Advanced configuration](#advanced-configuration)
    - [Models](#models)
      - [Inheriting from the Model Class](#inheriting-from-the-model-class)
      - [Custom LLM Call Function](#custom-llm-call-function)
      - [Custom Response Handling Function](#custom-response-handling-function)
      - [Example Usage](#example-usage-1)
    - [Prompts](#prompts)
      - [Edit the prompt](#edit-the-prompt)
      - [Show me the prompt !](#show-me-the-prompt-)
  - [References](#references)

---

## Get Started

For each part, you'll find functional examples to illustrate the features. If you have any questions, don't hesitate to visit the “Discussion” tab on GitHub.

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

## Reasoning models

When you use reasoning models like DeepSeek-R1, you need to disable JSON mode as the model will first output its chain of thought before producing the JSON. It is also a good idea to increase the timeout.

```python
r1_650b_azure = Model(
        base_url="https://DeepSeek-R1-lfvng.eastus.models.ai.azure.com/v1/chat/completions",
        model="DeepSeek-R1",
        timeout=180,
        json_output=False,
        api_key="..."
        )
        
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

ret = find_name_age("the captain's age is one year more than the cabin boy's, who is 22 years old", {"captain": 0, "cabin boy": 0})
print(ret)
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


## Asynchronous Mode

`emulate` can also be used in asynchronous mode. This can be useful if you want to use OpenHosta in a web application or a bot.

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

- `emulate`
- `ask`
- `thinkof`
- `predict`
- `generate_data`

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

## `predict` Function

The `predict` function is the second main feature of OpenHosta ! This function allows you to create **specific neural networks** based on the specifications you provide. Here's a breakdown to help you understand it:



The `predict` function can be used in function or class method by simply returns it. Its primary goal is to create a model tailored to the function it is called in. Currently, it supports two model types:

- **Linear Regression**: For prediction tasks by simply returns an `int`or a `float` :
  ```python
  from OpenHosta import predict, config
  
  def example_linear_regression(years : int, profession : str) -> float:
      """
      this function predict the salary based on the profession years.
      """
      return predict(verbose=2)
  
  print(example_linear_regression(1, "engineer"))
  ```
- **Classification**: For classifying multiple values among predefined categories in a `Literal` from the typing module :
  ```python
  from typing import Literal
  from OpenHosta import predict, config

  output = Literal["Good", "Bad"]
  
  def example_classification(word: str) -> output:
      """
      this function detects if a words is good or bad
      """
      return predict(verbose=2)
  
  print(example_classification("Bad"))
  ```

The `predict` function currently supports only the following return types: `int`, `float`, and `str`.

Additionally like you can see, `predict` can generate a dataset if none is provided in the [PredictConfig](#predictconfig-class), allowing users to see how a large language model (LLM) understands the problem and generates relevant data. By default, the data generation uses GPT-4o by OpenAI, the same oracle used in the [emulate](#emulate-function) function .



### Parameters
The `predict` function supports the following parameters:

- `verbose`: Controls the level of output information:
  - `0`: No output.
  - `1`: Basic output (default).
  - `2`: Detailed output.



- `oracle`: Specifies the model used for data generation. If set to `None`, no model will be used to handle missing data generation.

- `config`: Accepts a `Predictconfig` object for advanced configuration of model creation.

## `PredictConfig` class

The `PredictConfig` class provides advanced options for configuring the creation and management of *predict* models. Here’s a detailed breakdown:

```python
from OpenHosta import PredictConfig

model_config = PredictConfig(
    name="model_test",
    path="./__hostacache__",
    complexity=5,
    growth_rate=1.5,
    coef_layers=100,
    epochs=100,
    batch_size=32,
    max_tokens=1,
    dataset_path="./path_to_dataset.csv",
    generated_data=100,
    normalize=False
)
```

### Features

#### **Path Management**
- `path` (`str`): Specifies where data will be stored. Default: `./__hostacache__/`.
- `name` (`str`): Sets the directory name for storing model-related information. Default: the name of the Hosta-injected function.

#### **Architecture Configuration**
- `complexity` (`int`): Adjusts the model's complexity by adding or removing layers. Default: `5`.
- `growth_rate` (`float`): Determines the rate of increase in layer size. Default: `1.5`.
- `coef_layers` (`int`): Defines the maximum possible layer size based on the highest value between inputs and outputs. Default: `100`.

#### **Training Configuration**
- `normalize` (`bool`) : Specify if the data for training need to be normalize between -1 and 1. Default False, only possible with **Linear Regression** models
- `epochs` (`int`): Sets the number of training iterations. Default: calculated based on dataset size and batch size.
- `batch_size` (`int`): Specifies the number of examples processed before weight updates. Default: 5% of the dataset size if possible.

#### **Dataset Management**
- `max_tokens` (`int`): Limits the number of words a `str` input can contain, as the model adapts neuron sizes accordingly. Default: `1`.
  - **Warning**: Current model architectures do not perform well with natural language processing tasks. For such cases, use the *emulate* feature instead. NLP architecture support is coming soon.
- `dataset_path` (`str`): Provides a custom dataset path. Default: `None`, 
  - **Warning**: Only `csv` and `jsonl` files are supported for now. Please set the prediction columns to `outputs`.
- `generated_data` (`int`): Specifies the target number of data points for LLM generation (approximate). Default: `100`.

---

### Example Usage

```python
from OpenHosta import predict, PredictConfig

# Configuring the model
config_predict = PredictConfig(
    path="./__hostacache__",
    name="test_openhosta",
    complexity=5,
    growth_rate=1.5,
    coef_layers=100,
    normalize=False,
    epochs=45,
    batch_size=64,
    max_tokens=1,
    dataset_path="./path_to_your_dataset.csv"
)

# Using the predict function with the configuration
def demo_open_hosta(number: int, message: str) -> int:
    """
    this function is just here for an example :)
    """
    return predict(config=config_predict, oracle=None, verbose=2)

print(demo_open_hosta(42, "Hello World!"))
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
You can retrieve the predicted return type with the `return_type()` function:

```python
from OpenHosta import thinkof, return_type

x = thinkof("Adds all integers")
ret = x(2 ,3 ,6)
print(return_type(x)) # int
```

**Note** : ***this feature uses the default model.***

## `ask` function

The function `ask` is a sort of a *side* function In OpenHosta. Its only use is to make a simple LLM call without the OpenHosta's meta-prompt. It simplies the process af an API call.

```python
from OpenHosta import ask, Model

print(
    ask(
        system="You're a helpful assistant.",
        user="Write me a cool story.",
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

## `generate_data` function

Generate a dataset based on a given function and the number of samples. This function uses a synthetic data generator to create realistic input-output pairs for a given callable Python function based on its defined parameters, examples, and return type.

### Parameters

- **`function_pointer`** (`Callable`):  
  The target function used to generate the dataset. This function must take specific inputs and return outputs to be used for creating the dataset.  
  Proper type annotations and a clear docstring for the `function_pointer` are recommended to enhance the quality of generated data.

- **`num_samples`** (`int`):  
  The number of samples to generate. If the number exceeds 100, the function intelligently splits the data requests into manageable chunks.

- **`oracle`** (`Optional[Model]`, Optional):  
  The model or "oracle" used to assist with generating synthetic data.  
  By default, the function uses the system's predefined default model.

- **`verbose`** (`Union[Literal[0, 1, 2], bool]`, default=`2`):  
  Defines the verbosity level for logging the data generation process:  
  - `0` or `False`: No logging.
  - `1`: Minimal logging.
  - `2` or `True`: Detailed logging, providing insights during data generation.

### Returns

- **`HostaDataset`**:  
  An instance of `HostaDataset`, representing the generated dataset. This dataset can be saved to disk (CSV, JSON, JSONL) or iterated over for input-output pairs.

### Raises

- **`TypeError`**:  
  Raised if the provided `function_pointer` is not callable or lacks sufficient information to generate data (such as missing type annotations).

### Example

The following example demonstrates how to define a function, generate synthetic data using `generate_data`, and save the resulting dataset.

```python
from typing import Literal
from OpenHosta import generate_data, HostaDataset, example, emulate, SourceType

def detect_mood(message: str) -> Literal["positive", "negative", "neutral"]:
    """
    Analyze the mood conveyed in a text message.
    """
    # Provide pre-defined examples to guide synthetic data generation
    example(message="I feel lonely...", hosta_out="negative")
    example(message="I am happy!", hosta_out="positive")
    example(message="I have a cat", hosta_out="neutral")
    return emulate()

# Generate a dataset with 50 examples
dataset: HostaDataset = generate_data(detect_mood, 50)

# Save the dataset as a CSV file
dataset.save("detect_mood.csv", SourceType.CSV)

# Print each input-output pair in the dataset
correct = 0

for data in dataset.data:
    print(data.input[0].strip('"')+ f"expected {data.output} got " + detect_mood(data.input[0].strip('"')))
    if data.output == detect_mood(data.input[0].strip('"')):
        correct += 1

print(f"Accuracy: {correct}/{len(dataset.data)}, {correct/len(dataset.data)*100}%")
```

### How It Works

- **Define the Function**:  
  The target function (`detect_mood` in the example) must be well-defined, preferably with type annotations and examples to guide the data generation process.
- **Generate Synthetic Data**:
  Use `generate_data` to produce a dataset by specifying the number of samples and optionally overriding the default model with a custom `oracle`.
- **Save or Process Dataset**:  
  The returned dataset (`HostaDataset` instance) provides methods to save it in various formats (CSV, JSON, JSONL) or iterate over its contents for further analysis.

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
from typing import Dict, List
from OpenHosta import Model

class MyModel(Model):
    def api_call(
        self,
        messages: List[Dict[str, str]],
        json_output: bool = True,
        **llm_args
    ) -> Dict:
        # Your code here
        # Call the LLM and return the response
        return response
```

In the example above, we have overridden the "api_call" method of the Model class to create our own LLM call function.
The "api_call" method takes four arguments:

- **message**: The parsed message sent to the LLM.
- **json_output**: A boolean enabling the json format return option in the LLM call.
- **llm_args**: All the options given by the LLM's distributor. (ex. max_token, temperature, top_p...)

The "api_call" method returns a response object that contains the LLM's response to the user prompt.

#### Custom Response Handling Function

To create your own response handling function, you need to override the "response_parser" method of the Model class. This method is called every time the library receives a response from the LLM.

```python
from typing import Dict, Any
from OpenHosta import Model, FunctionMetadata, TypeConverter

class MyModel(Model):
    def response_parser(self, response: Dict, function_metadata: FunctionMetadata) -> Any:
        # Your code here
        # Process the LLM response and return the result
        return TypeConverter(function_metadata, l_ret_data).check()
```

In the example above, we have overridden the `response_parser` method of the Model class to create our own response handling function. 
The "response_parser" method takes three arguments:

- **response**: The response object returned by the LLM.
- **function_metadata**: The object containing all the useful information about the emulated function.

The "response_parser" method returns the processed return value. This is the value returned by the emulated function.

#### Example Usage

You can now create an instance of the class you've just created and use it in all OpenHosta's features.

With this method, you can now make OpenHosta compatible with a large number of API.

**Here's an example of of a custom Model class for Llama models:**

```python
from typing import Any, Dict, List
from OpenHosta import emulate, Model, TypeConverter, FunctionMetadata, example
from OpenHosta.utils.errors import RequestError
import requests
import json
import sys

class LlamaModel(Model):
    
    def __init__(self, model: str = None, base_url: str = None, api_key: str = None, timeout: int = 30):
        super().__init__(model, base_url, api_key, timeout)
        
    def api_call(self, messages: List[Dict[str, str]], json_output: bool = True, **llm_args) -> Dict:
        l_body = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        headers = {
            "Content-Type": "application/json"
        }
 
        if json_output:
            l_body["format"] = "json"
        for key, value in llm_args.items():
            l_body[key] = value
        try:
            response = requests.post(self.base_url, headers=headers, json=l_body, timeout=self.timeout)

            if response.status_code != 200:
                response_text = response.text
                raise RequestError(
                    f"[Model.api_call] API call was unsuccessful.\n"
                    f"Status cod: {response.status_code }:\n{response_text}"
                )
            self._nb_requests += 1
            return response.json()
        except Exception as e:
            raise RequestError(f"[Model.api_call] Request failed:\n{e}\n\n")
        
    def response_parser(self, response: Dict, function_metadata: FunctionMetadata) -> Any:
        json_string = response["message"]["content"]
        try:
            l_ret_data = json.loads(json_string)
        except json.JSONDecodeError as e:
            sys.stderr.write(
                f"[Model.response_parser] JSONDecodeError: {e}\nContinuing the process.")
            l_cleand = "\n".join(json_string.split("\n")[1:-1])
            l_ret_data = json.loads(l_cleand)
        return TypeConverter(function_metadata, l_ret_data).check()
        

mymodel = LlamaModel(
    model="llama3.2:1B",
    base_url="http://localhost:11434/api/chat",
    api_key="..."
)

def capitalize(sentence:str)->str:
    """
    This function capitalize a sentence in parameter.
    """
    example(sentence="foo bar", hosta_out="Foo Bar")
    return emulate(model=mymodel)


print(capitalize("hello world!"))
```

If the API request model is similar to OpenAI API, it can also work without class inheritance.

**Another example to work with Ollama:**

```python
from OpenHosta import config, ask

ollama_local_model=config.Model(
    model="gemma2:9b",
    base_url="http://localhost:11434/v1/chat/completions",
    api_key="not-empty-string"
)
config.set_default_model(ollama_local_model)

ask("hello")
```

**Now with Microsoft Azure:**

```python
from OpenHosta import config, ask

azure_model=config.Model(
    model="gpt-4o",
    base_url="https://YOUR_RESOURCE_NAME.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT_NAME/chat/completions?api-version=2024-06-01",
    api_key="Provide Azure OpenAI API key here"
)
config.set_default_model(azure_model)

ask("hello")
```

### Prompts

#### Edit the prompt

`emulate` works by putting the emulated function's parsed data in a meta-prompt in jinja2 designed to give the best performance and ensure a constant ouptput format.

You can find the prompt template at [meta_prompt.py](../src/OpenHosta/utils/meta_prompt.py) file.

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

