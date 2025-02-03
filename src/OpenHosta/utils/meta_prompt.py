from typing import Callable
from jinja2 import Template

class Prompt(Template):
    """
    Jinja2 compatible template.

    To create your own prompt:
    `my_prompt = Prompt('''Try to produce a JSON that answer this call:''')`
    
    To see the original prompt:
    `print(my_prompt)`
    """

    def __init__(self, source, *args, **kargs):
        super(Template, self).__init__()

        self.source = source

    def __str__(self):
        return self.source

    def __repr__(self):
        return f"""\
{type(self)}
source=
{self.source}"""

EMULATE_PROMPT=Prompt("""\
## Context

You will act as an emulator of impossible-to-code functions.
I will provide you with the description of the function using Python's way of declaring functions,
but I won't provide the function body as I don't know how to code it.
It might even be impossible to code. Therefore, you should not try to write the body.
Instead, imagine the function output.

In the conversation, I will directly write the function call as if it was called in Python.
You should answer with whatever you believe would be a good return for the function.

You should encode the returned value according to the provided JSON format, without comments. 
If you need to think first, place your thought within <think></think> before answering.
Answer using the following format:
```
{"return":"..."}
```

The output must be of the same type as that specified in the function call.
If you don't have enough information or don't know how to answer, the output should be “None”.

Any assumptions made should be reasonable based on the provided function description and should take into account the error handling of the function.
                            
{% if CTX_EXAMPLE %}
## Examples

**Example function definition:**

```python
def example_function(a: int, b: dict) -> int:
    \"\"\"
    This is an example function.
    It adds two numbers.
    \"\"\"
    return emulate()
```

---
{% endif %}{% if PRE_DEF %}
Here's the function definition:
{{ PRE_DEF }}
{% endif %}{% if PRE_SCHEMA %}
As you return the result in JSON format, here's the schema of the JSON object you should return:
{{ PRE_SCHEMA }}
{% endif %}{% if PRE_LOCALS %}
Here's the function's locals variables which you can use as additional information to give your answer:
{{ PRE_LOCALS }}
{% endif %}{% if PRE_SELF %}
Here's the method's class attributs variables which you can use as additional information to give your answer:
{{ PRE_SELF }}
{% endif %}{% if PRE_EXAMPLE %}
Here are some examples of expected input and output:
{{ PRE_EXAMPLE }}
{% endif %}{% if PRE_COT %}
To solve the request, you have to follow theses intermediate steps. Give only the final result, don't give the result of theses intermediate steps:
{{ PRE_COT }}
{% endif %}                                         
""")


THOUGHT_PROMPT = Prompt("""\
You will act as an emulator of impossible-to-code functions. 
I will provide you with the description of the function using Python's way of declaring functions, 
but I won't provide the function body as I don't know how to code it. 
It might even be impossible to code. Therefore, you should not try to write the body. 
Instead, directly imagine the function output.

In the conversation, I will directly write the function behavior as a sentence, and the argument passed to the function.

Your objective is to find the Python data type to be returned by the function. 
Take into account the function's behavior, the wording and intent of the sentence, and the arguments given.
You must give your answer without any comment and in the following JSON schema:
```
{\"type\": \"\"}
```

---

To fill in the type key, you need to follow Python syntax, such as "int" or "str", depending on your answer.

To solve the request, you have to follow theses intermediate steps. Give only the final result, don't give the result of theses intermediate steps:
Here are a few examples:

Function behavior: "Is a positive number"
Argument: 2
Expected response: {"type": "bool"}

Function behavior: "Multiply a number by 2"
Argument: 10
Expected response: {"type": "int"}

Function behavior: "Reverse a string"
Argument: "Hello World!"
Expected response: {"type": "str"}

Function behavior: "Sorts a list in ascending order"
Argument: (10, 5, 7, 12, 3)
Expected response: {"type": "list"}
                            
{% if CTX_EXAMPLE %}
{{ CTX_EXAMPLE }}
{% endif %}                              
""")

def print_last_prompt(function_pointer:Callable):
    """
    Print the last prompt sent to the LLM when using function `function_pointer`.
    """
    if hasattr(function_pointer, "_last_request"):
        if "sys_prompt" in function_pointer._last_request:
            print("[SYSTEM PROMPT]")
            print(function_pointer._last_request["sys_prompt"])
        if "user_prompt" in function_pointer._last_request:
            print("[USER PROMPT]")
            print(function_pointer._last_request["user_prompt"])
    else:
        print("No prompt found for this function.")


def print_last_response(function_pointer:Callable):
    """
    Print the last answer recived from the LLM when using function `function_pointer`.
    """
    if hasattr(function_pointer, "_last_response"):
        if "rational" in function_pointer._last_response:
            print("[THINKING]")
            print(function_pointer._last_response["rational"])
        if "answer" in function_pointer._last_response:
            print("[ANSWER]")
            print(function_pointer._last_response["answer"])
        if "data" in function_pointer._last_response:
            print("[Data]")
            print(function_pointer._last_response["data"])
        else:
            print("[UNFINISHED]")
            print("answer processing was interupted")
    else:
        print("No prompt found for this function.")
