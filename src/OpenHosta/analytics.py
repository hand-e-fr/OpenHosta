from transformers import GPT2Tokenizer, logging
from transformers import logging
from enum import Enum
import sys

logging.set_verbosity_error()

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")


class ModelType:
    BEST = "gpt4o"
    FAST = "gpt4o"
    CHEAP = "gpt4o"
    SECURE = "gpt4o"
    

class Analizer:
    
    _default_model:str = ModelType.BEST
    _model_list:list = (ModelType.BEST, ModelType.FAST, ModelType.CHEAP, ModelType.SECURE)
    
    def __init__(self, model:str=None):
        self.model = self._default_model if model is None else model
        if model not in self._model_list:
            sys.stderr.write(f"[ANALIZE_ERROR] Invalid model \"{model}\", rempplaced by best performance model \"{ModelType.BEST}\".")
            self.model = self._default_model


class Cost:
    
    _default_input_cost = 0.005
    _default_output_cost = 0.015
    
    def __init__(self, input_cost:int=None, output_cost:int=None):
        self.input = self._default_input_cost if input_cost is None else input_cost
        self.output = self._default_output_cost if output_cost is None else output_cost
        
    def get_input_cost(self):
        return self.input
    
    def get_output_code(self):
        return self.output

g_cost:dict = {"gpt4o": Cost(0.005, 0.015)}

print(g_cost["gpt4o"].get_input_cost())
print("gpt4o" in ModelType)

"""
def estimate_request_cost(input_text, estimated_output_token, model):
    input_tokens = tokenizer.encode(input_text)
    num_input_tokens = len(input_tokens)
    num_output_tokens = estimated_output_tokens
    if (model == "gpt4o"):
        cost_input = (num_input_tokens / 1000) * COST_PER_1000_INPUT_TOKENS
        cost_output = (num_output_tokens / 1000) * COST_PER_1000_OUTPUT_TOKENS
        total_cost = cost_input + cost_output
    return total_cost

input_text = "Bonjour, comment ça va aujourd'hui ?"
estimated_output_tokens = 8

cost, num_input_tokens, num_output_tokens = estimate_request_cost(input_text, estimated_output_tokens)

print(f"Nombre de tokens d'entrée : {num_input_tokens}")
print(f"Nombre de tokens de sortie estimé : {num_output_tokens}")
print(f"Coût total estimé : ${cost:.5f}")
"""