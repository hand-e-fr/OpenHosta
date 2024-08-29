import tiktoken
from enum import Enum
import time as t
import sys
import requests
import json

from config import Model

_estimate_prompt = """
You're a prompt engineering engineer tasked with estimating the number of output tokens an AI would return when executing a given function. The functions are written in Python, so function returns must use Python typing. 

Each time, I'll give you the following elements:
- The definition of the function.
- Its call with arguments. 
- The function's docstring.

You need to take all these elements into account when formulating your answer. To estimate the output token, you need to use a tokenization algorithm: take the one in GPT-3.

To make your estimate, you need to go through this chain of thought:

1. Understand the Function.
	- With the given definition, the function prototype and its docstring.
2. Analyze the Function Call.
	- With the function name and arguments provided.
3. Guess the expected result without calculating it.
	- You MUST NOT calculate the result of the function. - Simply make a prediction with all the elements you have at your disposal.
	- Pay attention to the type of output. If it's not specified in the function prototype, then guess it based on the description and type of the input arguments.
4. Estimate the number of tokens.
	- Use the information you have available for this step.
	- If the estimate is complex or impossible, make a realistic prediction using the context elements.
5. Formulate your answer
	- Synthesize your answer into a single number.
	- Follow the answer format I'll give you below

You should encode your response in valid JSON format, without comments, using the following format:
{ “tokens”:...}
Your answer in the “tokens” category must be a number only. Nothing should appear other than this JSON structure.

Any assumptions made should be reasonable based on the provided function description and should take into account the error handling of the function.

I'll give you a example:
Function definition:
```python
def reverse_string(a:str)->str:
	\"\"\"
	This function reverse the string in parameter.
	\"\"\"
	return emulate()
```

Function call:
```python
reverse_string("Hello World!")
```

Excpected output:
```
{"tokens": 13}
```

Here's all the function documentation for you to estimate:
"""

_g_model = "gpt-4o"
_g_apiKey = "sk-proj-T7o4z8S4q9fnBNTdSq4iT3BlbkFJ82uVDLRaIAkx1sjwyE5C"
    
class ModelAnalizer(Model):
    
    _default_input_cost:int = 0.005
    _default_output_cost:int = 0.015
    _default_token_perSec = 63.32
    _default_latency = 0.48
    
    def __init__(self, 
                 name:str,
                 input_cost:float,
                 output_cost:float, 
                 latency:float, 
                 token_perSec:float,
        ):
        self.name = self._default_name if name is None else name
        self.input_cost = self._default_input_cost if input_cost is None else input_cost
        self.output_cost = self._default_output_cost if output_cost is None else output_cost
        self.latency = self._default_latency if latency is None else latency
        self.token_perSec = self._default_token_perSec if token_perSec is None else token_perSec
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def get_input_cost(self):
        return self.input_cost
    
    def get_output_cost(self):
        return self.output_cost
    
    def get_latency(self):
        return self.latency
    
    def get_token_perSec(self):
        return self.token_perSec

    def _estimate_output_token(self, function_doc:str, function_call:str):
        global _estimate_prompt, _g_model, _g_apiKey
            
        try:
            if not _estimate_prompt or not _g_model or not _g_apiKey:
                raise ValueError("ValueError -> emulate empty values")
        except ValueError as v:
            sys.stderr.write(f"[ESTIMATE_ERROR]: {v}")
            return None
        
        api_key = _g_apiKey
        l_body = {
            "model": _g_model,
            "messages": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": _estimate_prompt
                            + "---\n"
                            + str(function_doc)
                            + "\n---",
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [{"type": "text", "text": str(function_call)}],
                },
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
            "top_p": 0.1,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions", json=l_body, headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            json_string = data["choices"][0]["message"]["content"]
            try:
                l_ret_data = json.loads(json_string)

            except json.JSONDecodeError as e:
                sys.stderr.write(f"JSONDecodeError: {e}")
                l_cleand = "\n".join(json_string.split("\n")[1:-1])
                l_ret_data = json.loads(l_cleand)

            l_ret = l_ret_data["tokens"]
        else:
            sys.stderr.write(f"Error {response.status_code}: {response.text}")
            l_ret = None

        return l_ret
        
    def _compute_request_cost(self, input_text, output_token):
        input_tokens = self.tokenizer.encode(input_text)
        num_input_tokens = len(input_tokens)
        num_output_tokens = output_token
        cost_input = (num_input_tokens / 1000) * self.input_cost
        cost_output = (num_output_tokens / 1000) * self.output_cost
        total_cost = cost_input + cost_output
        return total_cost
    
    def _compute_request_duration(self, output_token):
        total = self.latency
        total += self.token_perSec / output_token
        total += 0.5 # Processing duration margin
        return total

def request_timer(func):
    def wrapper(*args, **kwargs):
        g_c = '\033[94m'
        n = '\033[0m'
        bold = '\033[1m'
        
        start = t.time()
        rv = func(*args, **kwargs)
        end = t.time()
        
        duration = end - start
        print(f"{g_c}{bold}Execution time of {func.__name__}: {duration:.2f}s{n}")
        return rv
    return wrapper