import requests
import json
import sys
import inspect

enhancer_pre_prompt: str = """
I want you to become my Expert Prompt Creator for developer.
Your goal is to help me craft the best possible prompt for my programming needs.
The prompt you provide should be written from the perspective of me making the request to GPT-4o.
Consider in your prompt creation that this prompt will be entered into an interface for GPT-4o.
Apart from diagrams, you must write in text, without following any syntax.
The process is as follows:

You will generate the following sections:

"
-> enhanced:
{provide the best possible prompt according to my request. The prompt is used to describe
a function to be performed in Python as precisely as possible. You can add error handling,
as the function needs it to work properly. But don't code the function in the prompt.
The prompt should not tell to create the function, but describe how it works.}

-> critique:
{provide a concise paragraph on how to improve the prompt. Be very critical in your response.
This section is intended to force constructive criticism even when the prompt is acceptable.
Any assumptions and or issues should be included. Don't forget that you speak to a developer}

-> suggested:
{rewrite the prompt with the suggested improvements you made in the critique category.
The aim is to make a proposal, an example. Make logical assumptions to solve
the problem based on the context and all the information you have. You have to respond
to the problems you formulated in the previous category. But don't code the function
in the prompt.}

-> mermaid:
{Make a mermaid diagram explaining the function described by the prompt. You need to break
the reasoning into several steps for ease of understanding and clarity. You must
make it logical and easy to look at. You have to write it in mermaid syntax.
You must not use the markdown syntax}
"
"""


class enhancer:
    __last_enh_return__: str = None
    __last_enh__: dict = {
        "enhanced": None,
        "critique": None,
        "suggested": None,
        "mermaid": None,
    }

    _default_api_key: str = "sk-proj-T7o4z8S4q9fnBNTdSq4iT3BlbkFJ82uVDLRaIAkx1sjwyE5C"
    _default_ai_model: str = "gtp-4o"
    _default_creativity: float = 0.5
    _default_diversity: float = 0.5

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        creativity: float = None,
        diversity: float = None,
    ) -> None:
        self.api_key = enhancer._default_api_key if api_key == None else api_key
        self.model = enhancer._default_ai_model if model == None else model
        self.temperature = (
            enhancer._default_creativity if creativity == None else creativity
        )
        self.top_d = enhancer._default_diversity if diversity == None else diversity

    def ai_call_enh(self, sys_prompt: str, func_prot: str, func_doc: str):
        api_key = self.api_key
        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        data = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": [{"type": "text", "text": sys_prompt}]},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "\nHere's my python function's prototype:\n---\n"
                            + func_prot
                            + "\n---\n",
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "\nHere's my python function's prompt:\n---\n"
                            + func_doc
                            + "\n---\n",
                        }
                    ],
                },
            ],
            "temperature": self.temperature,
            "top_p": self.temperature,
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            response_data = response.json()
            return response_data["choices"][0]["message"]["content"]
        else:
            sys.stderr.write(
                "[CALL_ERROR] The request was unsuccessful or one of the parameters is invalid"
            )
            sys.stderr.write(f"Status: {response.status_code}")
            return None

    def parse_data(self, response: str):
        current_section = None
        current_text = []

        for line in response.splitlines():
            if line.startswith("->"):
                if current_section:
                    self.__last_enh__[current_section] = "\n".join(
                        current_text
                    ).strip()
                current_section = line[3:].strip(":")
                current_text = []
            else:
                current_text.append(line)
        if current_section:
            self.__last_enh__[current_section] = "\n".join(current_text).strip()

    def create_mermaid_file(self, mmd_script: str, name: str) -> None:
        if not mmd_script:
            raise ValueError("[MMD_ERROR] ValueError -> mmd_script")
        if not name:
            raise ValueError("[MMD_ERROR] ValueError -> mmd_script")

        try:
            with open(f"{name}_diagram.mmd", "w") as file:
                try:
                    file.write(mmd_script)
                except:
                    sys.stderr.write(
                        "[MMD_ERROR] An error occured when writing .mmd file"
                    )
        except IOError as e:
            sys.stderr.write(f"[MMD_ERROR] {e}")

    def create_help_file(
        self, name: str, enhanced: str, critique: str, suggested: str
    ) -> None:
        if not enhanced and not type(enhanced) == str:
            raise ValueError("[ENH_ERROR] ValueError -> enhanced")
        if not critique and not type(critique) == str:
            raise ValueError("[ENH_ERROR] ValueError -> critique")
        if not suggested and not type(suggested) == str:
            raise ValueError("[ENH_ERROR] ValueError -> suggested")

        try:
            with open(f"{name}_enhanced.md", "w") as file:
                try:
                    file.write("# ENHANCER\n")
                    file.write(f"- **Enhanced prompt:**\n{enhanced}\n")
                    file.write(f"- **How to improve your prompt:**\n{critique}\n")
                    file.write(f"- **Improvemed prompt suggestion:**\n{suggested}\n")
                except:
                    sys.stderr.write(
                        "[ENH_ERROR] An error occured when writing .mmd file"
                    )
        except IOError as e:
            sys.stderr.write(f"[ENH_ERROR] {e}")

    def enhance(self, func):
        def wrapper(*args, **kwargs):
            global enhancer_pre_prompt
            func_name, func_doc = func.__name__, func.__doc__

            sig = inspect.signature(func)
            func_prot = f"def {func_name} {sig}:\n"

            self.__last_enh_return__ = self.ai_call_enh(
                enhancer_pre_prompt, func_prot, func_doc
            )
            self.parse_data(self.__last_enh_return__)
            func.__doc__ = self.__last_enh__["enhanced"]
            self.create_mermaid_file(self.__last_enh__["mermaid"], func_name)
            self.create_help_file(
                func_name,
                self.__last_enh__["enhanced"],
                self.__last_enh__["critique"],
                self.__last_enh__["suggested"],
            )
            return self.__last_enh_return__

        return wrapper
