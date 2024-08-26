import os
import json
import sys

class PromptMananger:
    def __init__(self, json_path=None):
        if json_path is None:
            try:
                self.path = os.path.join(os.path.dirname(__file__), 'prompt.json')
            except Exception as e:
                self.path = ""
                sys.stderr.write(f"[JSON_ERROR] Impossible to find prompt.json:\n{e}")
                return
        else:
            self.path = json_path
        
        try:
            with open(self.path, 'r', encoding="utf-8") as file:
                self.json = json.load(file)
                self.prompts = {item['key']: item for item in self.json['prompts']}
        except FileNotFoundError:
            sys.stderr.write(f"[JSON_ERROR] File not found: {self.path}\n")
            self.prompts = {}
        except json.JSONDecodeError as e:
            sys.stderr.write(f"[JSON_ERROR] JSON decode error:\n{e}\n")
            self.prompts = {}
            
    def get_prompt(self, key):
        prompt = self.prompts.get(key)
        if prompt:
            return prompt['text']
        sys.stderr.write(f"[JSON_ERROR] Prompt not found\n")
        return None

    def get_prompt_details(self, key):
        prompt = self.prompts.get(key)
        if prompt:
            return prompt
        sys.stderr.write(f"[JSON_ERROR] Prompt not found\n")
        return None