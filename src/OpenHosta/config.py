import sys
import requests
import json
import re

def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

class Model():
    
    _SYS_PROMPT = ""
    
    def __init__(self, model:str=None, base_url:str=None, api_key:str=None):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        
        if any(var is None for var in (model, base_url)):
            sys.stderr.write(f"[CONFIG_ERROR] Empty values.")
            return
        elif not is_valid_url(self.url):
            sys.stderr.write(f"[CONFIG_ERROR Invalid URL.")
            return
            
    def __str__(self)->str:
        return (
            f"[OpenHosta] <{self.__class__.__module__}.{self.__class__.__name__} object at {hex(id(self))}>\n"
            f"Model: {self.model}\n"
            f"Base_url: {self.base_url}\n"
            "Infos:\n"
        )
        
    def _api_call(self, sys_prompt:str, user_prompt:str, creativity:float, diversity:float):
        if self.api_key is None or not self.api_key:
            sys.stderr.write(f"[CALL_ERROR] Unknown API key.")
            return
        
        l_body = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": str(sys_prompt)
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [{"type": "text", "text": str(user_prompt)}],
                },
            ],
            "response_format": {"type": "json_object"},
            "temperature": creativity if creativity is not None else 0.7,
            "top_p": diversity if diversity is not None else 0.7,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        
        try:
            response = requests.post(
                self.base_url, json=l_body, headers=headers
            )
        except Exception as e:
            pass
        if response.status_code != 200:
            sys.stderr.write(f"[CALL_ERROR] API call the request was unsuccessful.")
        return response
    
    def _request_handler(response):
        l_ret = ""
        
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


_default_model = Model(
    model="gpt-4o",
    base_url="https://api.openai.com/v1/chat/completions",
)    

def set_default_model(new:Model):
    global _default_model
    
    _default_model = new

# def set_id():
#     pass

# def set_parameter():
#     pass

def set_default_apiKey(api_key=None):
    global _default_model
    
    if api_key is not None or isinstance(api_key, str):
        _default_model.api_key = api_key
    else:
        sys.stderr.write("[CONFIG_ERROR] Invalid API key.")

__all__ = Model, _default_model, set_default_model, set_default_apiKey
