export MODEL_BASE_URL="https://aikit.webatt.fr/rtx3060/ollama/v1/chat/completions"
export MODEL_API_KEY="Basic ZWJhdHQ6UFM3cno0QTdja1VpTEt3VlNYa2VDTURZVnFXMHZ4cUw="



#########################################################
#
# Test model parameters
#
#########################################################

model.json_output=False
model.model = "RTX3060-simpo:9b"

sentence = capitalize_cities("je suis allé à paris en juin")
print_last_response(capitalize_cities)

from OpenHosta import Prompt

config.EMULATE_PROMPT
model.json_output=False
prompt = Prompt(
"""\
Start with a <think></think> tag and think about the problem. Then, write the function.
{% if PRE_DEF %}
Here's the function:
{{ PRE_DEF }}
{% endif %}
Answer in json unsigned this format:
{"return":"..."}
""")

def capitalize_cities(sentence:str)->str:
    """
    This function capitalize the first letter of all city names in a sentence.
    """
    return emulate(prompt=prompt)

sentence = capitalize_cities("je suis allé à paris en juin")
print_last_prompt(capitalize_cities)
print_last_response(capitalize_cities)
assert "Paris" in sentence

#########################################################
#
# Test Reasoning models
#
#########################################################




