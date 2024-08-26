import tiktoken
from enum import Enum
import time as t

class Models(Enum):
    BEST = "gpt-4o"
    FAST = "gpt-4o"
    CHEAP = "gpt-4o"
    SECURE = "gpt-4o"
    
class ModelAnalizer:
    
    _default_name:str = "Unknown"
    _default_input_cost:int = 0.005
    _default_output_cost:int = 0.015
    _default_token_perSec = 63.32
    _default_latency = 0.48
    _default_quality_score:int = 0
    _default_security_score:int = 0
    
    def __init__(self, 
                 name:str,
                 input_cost:float,
                 output_cost:float, 
                 latency:float, 
                 token_perSec:float,
                 quality_score:float,
                 security_score:float
                 ):
        self.name = self._default_name if name is None else name
        self.input_cost = self._default_input_cost if input_cost is None else input_cost
        self.output_cost = self._default_output_cost if output_cost is None else output_cost
        self.latency = self._default_latency if latency is None else latency
        self.token_perSec = self._default_token_perSec if token_perSec is None else token_perSec
        self.quality_score = self._default_quality_score if quality_score is None else quality_score
        self.security_score = self._default_security_score if security_score is None else security_score
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
           
    def get_name(self):
        return self.name
    
    def get_input_cost(self):
        return self.input_cost
    
    def get_output_cost(self):
        return self.output_cost
    
    def get_latency(self):
        return self.latency
    
    def get_token_perSec(self):
        return self.token_perSec
    
    def get_quality_score(self):
        return self.quality_score
    
    def get_security_score(self):
        return self.security_score
    
    def estimate_output_token(function_doc:str, function_call:str):
        pass
    
    def compute_request_cost(self, input_text, estimated_output_token, model):
        input_tokens = self.tokenizer.encode(input_text)
        num_input_tokens = len(input_tokens)
        num_output_tokens = estimated_output_token
        cost_input = (num_input_tokens / 1000) * self.input_cost
        cost_output = (num_output_tokens / 1000) * self.output_cost
        total_cost = cost_input + cost_output
        return total_cost

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