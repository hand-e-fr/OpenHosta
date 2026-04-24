from OpenHosta import emulate, config

config.DefaultModel.model_name="qwen3.5:4b"
config.DefaultModel.base_url="http://127.0.0.1:11434"
config.DefaultModel.api_parameters |= {"reasoning": {"effort": "none"}}

def answer_as_repl(request:str) -> str:
    """
    Answer the request as if you were in a REPL.
    """
    return emulate(force_llm_args={"assistant_starts_with":">>> "})


answer_as_repl("print('hello')")

from OpenHosta import print_last_prompt, print_last_decoding
print_last_prompt(answer_as_repl)
print_last_decoding(answer_as_repl)

def fill_dict_with(content:str)->dict:
    """
    Return the list of capitals as a dict[Country: Capital] with country and Capital as string.
    """
    return emulate(force_llm_args={"assistant_starts_with":'```python\n{'})

print(fill_dict_with("list of european capital cities"))
print_last_prompt(fill_dict_with)

