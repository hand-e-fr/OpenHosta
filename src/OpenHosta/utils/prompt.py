import os
import json
import sys

class PromptManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PromptManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, json_path=None):
        if self._initialized: return
        self._initialized = True
        if json_path is None:
            try:
                self.path = os.path.join(os.path.dirname(__file__), "prompt.json")
            except Exception as e:
                self.path = ""
                raise FileNotFoundError(f"[JSON_ERROR] Impossible to find prompt.json:\n{e}")
        else:
            self.path = json_path

    def get_prompt(self, key):
        with open(self.path, "r", encoding="utf-8") as file:
                jsonfile = json.load(file)
                prompts = {item["key"]: item for item in jsonfile["prompts"]}
        prompt = prompts.get(key)
        if prompt:
            return prompt["text"]
        sys.stderr.write(f"[JSON_ERROR] Prompt not found\n")
        return None

    def get_prompt_details(self, key):
        with open(self.path, "r", encoding="utf-8") as file:
                jsonfile = json.load(file)
                prompts = {item["key"]: item for item in jsonfile["prompts"]}
        prompt = prompts.get(key)
        if prompt:
            return prompt
        sys.stderr.write(f"[JSON_ERROR] Prompt not found\n")
        return None

    def set_prompt(self, name: str, category: str, version: str, filepath: str):
        new = {"key": "", "text": "", "category": "", "version": ""}

        with open(filepath, "r", encoding="utf-8") as file:
            prompt = file.read()
        with open(self.path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)

        new["key"], new["category"], new["version"] = name, category, version
        new["text"] = prompt

        found = False
        for elem in data["prompts"]:
            if elem["key"] == new["key"]:
                elem["text"] = new["text"]
                elem["version"] = new["version"]
                found = True
                break
        if not found:
            data["prompts"].append(new)
        with open(self.path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"{name} prompt has been added to {self.path}")

    def show_prompt(self, key):
        prompt = self.prompts.get(key)
        if prompt:
            print(prompt["text"])
            return prompt["text"]
        sys.stderr.write(f"[JSON_ERROR] Prompt not found\n")
        return None