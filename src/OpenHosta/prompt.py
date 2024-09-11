import os
import json
import sys


class PromptMananger:
    def __init__(self, json_path=None):
        if json_path is None:
            try:
                self.path = os.path.join(os.path.dirname(__file__), "prompt.json")
            except Exception as e:
                self.path = ""
                sys.stderr.write(f"[JSON_ERROR] Impossible to find prompt.json:\n{e}")
                return
        else:
            self.path = json_path

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                self.json = json.load(file)
                self.prompts = {item["key"]: item for item in self.json["prompts"]}
        except FileNotFoundError:
            sys.stderr.write(f"[JSON_ERROR] File not found: {self.path}\n")
            self.prompts = {}
        except json.JSONDecodeError as e:
            sys.stderr.write(f"[JSON_ERROR] JSON decode error:\n{e}\n")
            self.prompts = {}

    def get_prompt(self, key):
        prompt = self.prompts.get(key)
        if prompt:
            return prompt["text"]
        sys.stderr.write(f"[JSON_ERROR] Prompt not found\n")
        return None

    def get_prompt_details(self, key):
        prompt = self.prompts.get(key)
        if prompt:
            return prompt
        sys.stderr.write(f"[JSON_ERROR] Prompt not found\n")
        return None

    def set_prompt(self, name: str, category: str, version: str, filepath: str):
        json_filepath = "prompt.json"
        new = {"key": "", "text": "", "category": "", "version": ""}

        try:
            with open(filepath, "r", encoding="utf-8") as file:
                prompt = file.read()
        except FileNotFoundError:
            sys.stderr.write(f"File {filepath} not found.")
        except IOError as e:
            sys.stderr.write(f"File error: {e}")
        else:
            try:
                with open(json_filepath, "r", encoding="utf-8") as json_file:
                    data = json.load(json_file)
            except FileNotFoundError:
                sys.stderr.write(f"File {json_filepath} not found.")
            except IOError as e:
                sys.stderr.write(f"File error: {e}")
            except Exception as e:
                sys.stderr.write(e)
            else:
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

                try:
                    with open(json_filepath, "w", encoding="utf-8") as json_file:
                        json.dump(data, json_file, ensure_ascii=False, indent=4)
                except FileNotFoundError:
                    sys.stderr.write(f"File {json_filepath} not found.")
                except IOError as e:
                    sys.stderr.write(f"File error: {e}")
                except Exception as e:
                    sys.stderr.write(e)
                else:
                    print(f"{name} prompt has been added to {json_filepath}")

    def show_prompt(self, key):
        prompt = self.prompts.get(key)
        if prompt:
            print(prompt["text"])
            return prompt["text"]
        sys.stderr.write(f"[JSON_ERROR] Prompt not found\n")
        return None
