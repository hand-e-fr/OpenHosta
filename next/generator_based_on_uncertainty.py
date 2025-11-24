
from OpenHosta import OneTurnConversationPipeline, config, MetaPrompt
pipe = OneTurnConversationPipeline(model_list=[config.DefaultModel])

pipe.user_call_meta_prompt = MetaPrompt("""
{% if force_answer_start %}# Your answer has been truncated. This is a second attempt to complete it. Can you provide the full answer knowing that is started with {{ force_answer_start }}{% endif %}
{% if variables_initialization %}# Values of parameters to be used
{{ variables_initialization }}{% endif %}
{{ function_name }}({{ function_call_arguments }})
""")
    

@max_uncertainty()
def question(prompt:str)->str:
    """
    Answer to a question
    """
    return emulate(pipeline=pipe)

dir(question.hosta_injected)
question.hosta_injected.force_template_data = {"force_answer_start": None}
question.hosta_injected.force_template_data = {"force_answer_start": "'Emma"}

question("qui a été élu président de la république française en 2021 ?")

print_last_prompt( question )

# Convert token to token id using 
question.hosta_injected.force_llm_args = {"logit_bias": {}}

question.hosta_injected.force_template_data = {"force_answer_start": None}
question.hosta_injected.force_template_data = {"force_answer_start": '\'"p\''}
question("propose moi une couleur au hasard")
[(p["top_logprobs"][0]["token"], math.exp(p["top_logprobs"][0]["logprob"])) for p in question.hosta_inspection["logs"]["llm_api_response"]["choices"][0]["logprobs"]["content"] ]

for v in [[(x["token"],f"{math.exp(x["logprob"]):.4f}" ) for x in sorted(p["top_logprobs"], key=lambda item: item["logprob"], reverse=True)[:10]] for p in question.hosta_inspection["logs"]["llm_api_response"]["choices"][0]["logprobs"]["content"] ]:
    print(v)
    
print_last_prompt( question )

### This part is to test token ids retrieval from logprobs
# Conclusion, is only affects the token selection and does not change the displayed Logprobs

import os
from openai import OpenAI
import tiktoken

# Initialize Client
client = OpenAI(api_key=os.environ.get("OPENHOSTA_DEFAULT_MODEL_API_KEY"))

# 1. Define the model and get the correct encoding
MODEL = "gpt-4.1"

try:
    # Try to get the specific encoding for the model
    enc = tiktoken.encoding_for_model(MODEL)
except KeyError:
    # Fallback: GPT-4o and GPT-4.1 family typically use 'o200k_base'
    print(f"Warning: Encoding for {MODEL} not found. Defaulting to 'o200k_base'.")
    enc = tiktoken.get_encoding("o200k_base")

# 2. Make the API call with logprobs enabled
response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "name a color of the rainbow? Just answer with the color name. No explanation."}],
    logprobs=True,
    logit_bias={15957:-100}, 
    top_logprobs=20  # Request top 3 alternative tokens per position
)

print(f"Vocabulary size: {enc.n_vocab}")
import math
limit = math.log(1/enc.n_vocab)

# 3. Iterate through the response and retrieve Token IDs
if response.choices[0].logprobs:
    print(f"{'Position':<10} | {'Type':<10} | {'Token Text':<15} | {'Token ID':<10} | {'Logprob':<10}")
    print("-" * 65)

    for i, content in enumerate(response.choices[0].logprobs.content):
        # A. Process the chosen token
        chosen_token_str = content.token
        # encode() returns a list, usually length 1 for a single token output
        chosen_id = enc.encode(chosen_token_str)[0]
        
        # B. Process the top_logprobs (alternatives)
        for top in content.top_logprobs:
            if top.logprob < limit:
                break  # Skip low probability alternatives
            top_token_str = top.token
            # Map text back to ID
            top_id = enc.encode(top_token_str)[0]
            
            print(f"{'':<10} | {'ALT' if top_token_str!=chosen_token_str else 'CHOSEN':<10} | {repr(top_token_str):<15} | {top_id:<10} | {top.logprob:.4f}")
        
        print("-" * 65)