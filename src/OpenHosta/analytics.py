import tiktoken

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
                 url:str,
                 input_cost:float,
                 output_cost:float, 
                 latency:float, 
                 token_perSec:float,
                 quality_score:float,
                 security_score:float
                 ):
        self.name = self._default_name if name is None else name
        self.url = None if url is None else url
        self.input_cost = self._default_input_cost if input_cost is None else input_cost
        self.output_cost = self._default_output_cost if output_cost is None else output_cost
        self.latency = self._default_latency if latency is None else latency
        self.token_perSec = self._default_token_perSec if token_perSec is None else token_perSec
        self.quality_score = self._default_quality_score if quality_score is None else quality_score
        self.security_score = self._default_security_score if security_score is None else security_score
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
           
    def get_name(self):
        return self.name
    
    def get_url(self):
        return self.url
    
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
    
    def is_url_correct(self):
        return True
    
    def estimate_request_cost(self, input_text, estimated_output_token, model):
        input_tokens = self.tokenizer.encode(input_text)
        num_input_tokens = len(input_tokens)
        num_output_tokens = estimated_output_token
        cost_input = (num_input_tokens / 1000) * self.input_cost
        cost_output = (num_output_tokens / 1000) * self.output_cost
        total_cost = cost_input + cost_output
        return total_cost
        
Models:dict = {
    "BEST": ModelAnalizer(name="gpt-4o", url="url", input_cost=0.005, output_cost=0.015, latency=0.48, token_perSec=63.32, quality_score=1, security_score=0.2),
    # "FAST": ModelAnalizer(name="gpt-4o", url="url", input_cost=0.005, output_cost=0.015, latency=0.48, token_perSec=63.32, quality_score=1, security_score=0.2),
    # "CHEAP": ModelAnalizer(name="gpt-4o", url="url", input_cost=0.005, output_cost=0.015, latency=0.48, token_perSec=63.32, quality_score=1, security_score=0.2),
    "SECURE": ModelAnalizer(name="gpt-4o", url="url", input_cost=0.005, output_cost=0.015, latency=0.48, token_perSec=63.32, quality_score=1, security_score=0.2),
    }
    
print(Models["BEST"].get_name())
    
# class Cost:
    
#     _default_input_cost = 0.005
#     _default_output_cost = 0.015
    
#     def __init__(self, input_cost:int=None, output_cost:int=None):
#         self.input = self._default_input_cost if input_cost is None else input_cost
#         self.output = self._default_output_cost if output_cost is None else output_cost
        
#     def get_input_cost(self):
#         return self.input
    
#     def get_output_cost(self):
#         return self.output
    
#     def estimate_request_cost(self, input_text, estimated_output_token, model):
#         input_tokens = tokenizer.encode(input_text)
#         num_input_tokens = len(input_tokens)
#         num_output_tokens = estimated_output_token
#         cost_input = (num_input_tokens / 1000) * self.input
#         cost_output = (num_output_tokens / 1000) * self.output
#         total_cost = cost_input + cost_output
#         return total_cost
    
# class Speed:
    
#     _default_token_perSec = 63.32
#     _default_latency = 0.48
    
#     def __init__(self, latency:int=None, token_perSec:int=None):
#         self.latency = self._default_latency if latency is None else latency
#         self.token_perSec = self._default_token_perSec if token_perSec is None else token_perSec
        
#     def get_latency(self):
#         return self.latency
    
#     def get_token_perSec(self):
#         return self.token_perSec
    
# class Quality:
    
#     _default_MMLU_score = 0.864
#     _default_quality_index = 100
    
#     def get_quality_score(self):
#         pass

# class Security:
#     pass

# class Analizer:
    
#     __model_data__:dict = {"cost": None, 
#                            "duration": None, 
#                            "quality": None, 
#                            "secure": None}
    
#     _default_model:str = ModelType.BEST
#     _model_list:list = (ModelType.BEST, ModelType.FAST, ModelType.CHEAP, ModelType.SECURE)
    
#     def fill_model_data(model:str)->dict:
#         match model:
#             case ModelType.BEST:
#                 return {"cost": Cost(0.005, 0.015), "duration": Speed(0.48, 63.32), "quality": None, "security": "low"}
#             case ModelType.FAST:
#                 return {"cost": None, "duration": None, "quality": None, "secure": None}
#             case ModelType.CHEAP:
#                 return {"cost": None, "duration": None, "quality": None, "secure": None}
#             case ModelType.SECURE:
#                 return {"cost": None, "duration": None, "quality": None, "secure": None}
#             case _:
#                 sys.stderr.write(f"[ANALIZE_ERROR] Invalid model \"{model}\", remplaced by best performance model \"{ModelType.BEST}\".")
#                 return {"cost": Cost(None, None), "duration": Speed(None, None), "quality": None, "secure": None}
    
#     def __init__(self, model:str=None):
#         self.model = self._default_model if model is None else model
#         if model not in self._model_list:
#             sys.stderr.write(f"[ANALIZE_ERROR] Invalid model \"{model}\", remplaced by best performance model: \"{ModelType.BEST}\".")
#             self.model = self._default_model


