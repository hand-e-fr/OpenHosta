import json
import ast

class HostaInt:
    BASE_TYPE = int
    
    def python_schema_definition(self, variable_name:str):
        return f"{variable_name}:int"
    
    def json_schema_definition(self, variable_name:str):
        return f'"{variable_name}": {{"type": "integer"}}'
    
    def from_python_str(self, value:str):
        return int(value)
    
    def from_json_str(self, value:str):
        return int(value)
    
    def verify_json_schema(self, value:str):
        return json.loads(value)["type"] == "integer"
    
    def verify_python_language(self, value:str):
        # parse the value as python code and check if it is an integer
        is_parsed = ast.parse(value)
        return isinstance(is_parsed.body[0].value, ast.Num) and isinstance(is_parsed.body[0].value.n, int)
    
    def __init__(self, value:str):
        
        # test is value looks like python or json
        if self.verify_python_language(value):
            self.value = self.from_python_str(value)
        elif self.verify_json_schema(value):
            self.value = self.from_json_str(value)
        else:
            raise ValueError(f"Value {value} is not a valid integer")
        
    
