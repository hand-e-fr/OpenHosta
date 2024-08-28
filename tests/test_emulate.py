import sys

class BasicTestEmulate:
    
    def __init__(self, api_key:str=None):
        self.api_key = api_key
        if not api_key:
            sys.stderr.write("[TEST_ERROR] Invalid API key.")
            return
        
    
    def math_easy(self):
        pass
    
    def math_medium(self):
        pass
    
    def math_hard(self):
        pass
    
    def str_easy(self):
        pass
    
    def str_medium(self):
        pass
    
    def str_hard(self):
        pass
    
class RobustTestEmulate:
    
    def __init__(self, api_key:str=None):
        self.api_key = api_key
        if not api_key:
            sys.stderr.write("[TEST_ERROR] Invalid API key.")
            return