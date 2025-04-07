# This scripts test basic input and return types for many models

ModelList = [
    'chatgpt-4o-latest', 
    'codestral',
    # 'DeepSeek-R1-azure',
    # 'DeepSeek-R1-huggingface',
    # 'gemini-2.0-flash-thinking-exp-01-21', 
    'gemma2-9b-it', 
    'mistral-large-2407', 
    'mistral-small-2501',
    #'sonnet-3.5-v2',
    #'Qwen-QwQ-32B-huggingface',
    # 'RTX3060-qwen2.5-coder-14b',
    # 'claude-3-7-sonnet-20250219',
    # 'claude-3-7-sonnet-thinking', 
    # 'gemini-2-pro',
    # 'gpt-4.5-preview-2025-02-27', 
    # 'gpt-4o-2024-08-06',
    # 'llama-3.3-70b-cerebras',
    # 'llama-3.3-70b-groq',
    # 'o3-mini-high',
    # 'o3-mini-medium',
    # 'qwen-2.5-coder-32b',
    # 'safe.hf.co/bartowski/RekaAI_reka-flash-3-GGUF:IQ4_XS',
    'safe.RTX3060-gemma3:12b',
    # 'safe.gemma3:4b',
    'safe.phi4-mini:latest'
    ]

base_url = "https://chat.hand-e.cloud/api/chat/completions"
api_key = "sk-2063d493d39544089c3fe31f90d9b468"


#from OpenHosta.utils.meta_prompt import EMULATE_PROMPT
from OpenHosta.core.meta_prompt import Prompt
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
{% if NEED_THINKING %}If you need to think first, place your thought within <think></think> before answering.{% endif %}
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

If you need to say anything or assume anything before the JSON output, say it between <think></think> tags this way:
<think>
The user might want ...
</think>                                    
""")

from OpenHosta import OpenAICompatibleModel, config

model = OpenAICompatibleModel(
    model=ModelList[0],
    base_url=base_url,
    api_key=api_key,
    json_output=False)

config.set_default_model(model)

from OpenHosta import ask

ask("hello")

### Loop test all models

from OpenHosta import emulate, thought

def add_two(some_number:str)->int:
    """
    This function adds two to the some_number given in parameter
    """
    return emulate(prompt=EMULATE_PROMPT)

config._DefaultModelPolicy.model.model = 'chatgpt-4o-latest'
config._DefaultModelPolicy.model.json_output = False
add_two("cinq")
inspection = add_two.hosta_inspection

from OpenHosta import print_last_response
print_last_response(add_two)
add_two._last_response


prompt = EMULATE_PROMPT

prompt_data = gather_data_for_prompt_template(inspection)
prompt_rendered = prompt.render(prompt_data)
print(prompt_rendered)

from OpenHosta.exec.emulate import gather_data_for_prompt_template

async def run_test(model_name):
    model.model = model_name

    # print(prompt_rendered)
    # response_dict = model.api_call([
    #         {"role": "system", "content": prompt_rendered},
    #         {"role": "user", "content": inspection._infos.f_call}
    #     ]
    # )
    response_dict = await model.api_call_async([
            {"role": "system", "content": prompt_rendered},
            {"role": "user", "content": inspection._infos.f_call}
        ]
    )
    return response_dict

async def run_tests(model_name):
    co = [run_test(model_name) for x in range(10)]
    test_repetitions = await asyncio.gather(*co)
    return test_repetitions

import asyncio

results = {}

for model_name in ModelList:
    results[model_name] = []
    test_repetitions = asyncio.run(run_tests(model_name))

    for response_dict in test_repetitions:
        
        res = [None, None, None]
        results[model_name].append(res)

        try:
            res[0] = response_dict['choices'][0]["message"]["content"]
            res[1] = untyped_response = model.response_parser(response_dict, inspection._infos)
            res[2] = response_data = model.type_returned_data(untyped_response, inspection._infos)
        except:
            pass

        print(f"Call {model_name} : {res[2]}")

import pickle

import datetime

t = datetime.datetime.now().replace(microsecond=0).isoformat().replace(":", "")

with open(f"test_{inspection.infos.f_name}_{t}", "wb") as fp:
    test = {"inspection_infos": inspection._infos, 
            "results": results}
    pickle.dump(test, file=fp)

# import pickle
# with open(f"test_add_two_2025-03-22T183716", "rb") as fp:
#     test = pickle.load(fp)

for k,r in results.items():
    print(k,":")
    for v in r:
        print(v)

 