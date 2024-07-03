import inspect
import requests
import json
import openai

enhancer_pre_prompt:str = """
I want you to become my Expert Prompt Creator for developer.
Your goal is to help me craft the best possible prompt for my programming needs.
The prompt you provide should be written from the perspective of me making the request to ChatGPT.
Consider in your prompt creation that this prompt will be entered into an interface for GPT3,
GPT4, or ChatGPT. The prompt will include instructions to write the output using my communication
style. The process is as follows:

You will generate the following sections:

"
**Prompt:**
{provide the best possible prompt according to my request. The prompt is used to describe
a function to be performed in Python as precisely as possible. You can add error handling,
as the function needs it to work properly.}

**Critique:**
{provide a concise paragraph on how to improve the prompt. Be very critical in your response.
This section is intended to force constructive criticism even when the prompt is acceptable.
Any assumptions and or issues should be included. Don't forget that you speak to a devloper}

**Proposition:**
{rewrite the prompt with the suggested improvements in the critique category.
The aim is to make a proposal, an example. Make logical assumptions to solve
the problem based on the context and all the information you have.}

**Diagram:**
{Make a mermaid diagram explaining the function described by the prompt. You need to break
the reasoning into several steps for ease of understanding and clarity. You must
make it logical and easy to look at. You have to write it in mermaid syntax.}
"

Here's my python function's prototype:

Here's my python function's prompt:
"""

class enhancer:
    __last_prompt__:str = None
    __last_crit__:str = None
    __last_prop__:str = None
    __last_diag__:str = None
    __last_data__:dict = {"enchance_prompt": __last_prompt__, "Critique": __last_crit__,
                            "Proposition": __last_prop__, "Diagram": __last_diag__}

    _default_api_key:str = "sk-proj-T7o4z8S4q9fnBNTdSq4iT3BlbkFJ82uVDLRaIAkx1sjwyE5C"
    _default_ai_model:str = "gtp-4o"

    def __init__(self, api_key:str=None, model:str=None)->None:
        self.api_key = enhancer._default_api_key if api_key == None else api_key
        self.model = enhancer._default_ai_model if model == None else model
        self.temperature = 0.7
        self.top_d = 0.7

    def ai_call(self, prompt:str)->dict:
        openai.api_key = self.api_key
        try:
            response = openai.completions.create(
                model = self.model
                prompt = prompt
                temperature = self.temperature
                top_p = self.top_p
            )
        except:
