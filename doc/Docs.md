# Documentation
___

Documentation for version: **1.0**

Welcome to **OpenHosta** documentation :). Here you'll find all the **explanations** you need to understand the library, as well as **usage examples** and advanced **configuration** methods for the most complex tasks. You'll also find explanations of the source code for those interested in **contributing** to this project. Check the Jupyter Notebook **test files** to help you take your first steps in discovering OpenHosta.

For this project, we have adopted a [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a respectful and inclusive environment for all contributors. Please take a moment to read it.

___

### Introduction

#### First Step

OpenHosta is a **Python library** designed to facilitate the integration of **LLMs** into the developer's environment, by adding a layer to the Python programming language without distorting it. It is based on the **PMAC** concept, reimagining the **compilation** process in “Just-In-Time” languages. All our functionalities respect the **syntax and paradigm** of this language. 

The choice of LLM is mostly up to you, depending on your configuration level, moreover the vast majority are compatible. By default, OpenAI's **GPT-4o** is chosen. This has been tested by our team during development and **provides** a satisfaying level of functionality. 

Whatever your configuration, make sure you own a **working API key** before proceeding. Keep in mind that each request will incur **costs** which are different depending on the model. You can find prices on distributor websites. Here are the prices for the OpenAI API: https://openai.com/api/pricing/

We've already mentioned a few concepts about **AI** or **computer science**. If some of them are **unclear** to you, please have a look at the *“references”* section, where a series of explanatory links or definitions will be listed to **help** you understand.

Finally, if you like the project and are thinking of contributing, please refer to our [Contribution Guide](CONTRIBUTING.md)

#### Why use OpenHosta?

- **Beyond programming**

OpenHosta allows you to code functions that are complex or were impossible **before**, by supporting some ambiguities of **human language**. The processing of language relating to social codes or other parameters that are **difficult** to implement in Python for example. It **simplifies** tasks that would otherwise require significant time and expertise, thus expanding **possibilities** in Python programming.

- **Python Ecosystem**

OpenHosta integrates **fully** into Python syntax. Our main goal is to push programming to a **higher level**. For example, we send *docstrings*, commonly used in Python, to the **LLMs** context. We also integrate **advanced methods** such as *lambdas* and the compatibility with *Pydantic* typing. 

- **Open-Source**

We are an Open-Source project. We believe this philosophy contributes to the **sustainability** and **independence** of the artificial intelligence sphere. AI is a great **revolution**, so let's bring it **forward** in the best possible way. We count on your **feedback** and **contributions** to keep OpenHosta evolving.

---

Let's **get started**! First here's the **table of contents** to help you navigate through the various sections of the documentation.

### Table of Content

- [Documentation](#documentation)
    - [Introduction](#introduction)
      - [First Step](#first-step)
      - [Why use OpenHosta?](#why-use-openhosta)
    - [Table of Content](#table-of-content)
  - [Features](#features)
    - [OpenHosta Example](#openhosta-example)
    - [Get Started](#get-started)
      - [Librairie Import](#librairie-import)
      - [Basic Setup](#basic-setup)
    - ["emulate()" Function](#emulate-function)
    - [Pydantic Return](#pydantic-return)
    - ["enhance"](#enhance)
    - ["thought"](#thought)
  - [Advanced Configuration](#advanced-configuration)
    - ["Model" class](#model-class)
    - [Further Information](#further-information)
  - [Source Code Explanation](#source-code-explanation)
  - [Advanced Examples](#advanced-examples)
  - [Road Map \& Benchmark](#road-map--benchmark)
    - [References](#references)

---

## Features

### OpenHosta Example

For each part, you'll find functional examples to illustrate the features. If you have any questions, don't hesitate to visit the “Discussion” tab on GitHub.

### Get Started

Once you've installed the OpenHosta library, you're ready to get started. We'll import the library and then look at the basic configurations.

#### Librairie Import

```python
from OpenHosta import *
```

We recommend this import method, as it gives you all the important and stable features:
  - Emulate function
  - Thought function 
  - \_\_suggest\_\_ attributes
  - Configuration tools

But you can also import modules one by one.

```python
from OpenHosta import emulate, config
```

#### Basic Setup

This section focuses on the *config* module.

As previously mentioned, a default model is automatically assigned: GPT-4o. To use it, you first need to enter your API key.

```python
config.set_default_apiKey("put-your-api-key-here")
```

Once you've done that, all OpenHosta's features are ready to use.

If you wish to use another model, you'll need to create an instance of the *Model* class.

```python
my_model = config.Model(
    model="gpt-4o", 
    base_url="https://api.openai.com/v1/chat/completions"
    api_key="put-your-api-key-here"
)
```

Note that some features like *thought* or *\_\_suggest\_\_* specifically use the default model. So if you want to change it, use this.

```python
config.set_default_model(my_model)
```

### "emulate()" Function

### Pydantic Return 

### "enhance"

### "thought"

---

## Advanced Configuration

### "Model" class

### Further Information

---

## Source Code Explanation

---

## Advanced Examples

---

## Road Map & Benchmark

---

### References

---

---