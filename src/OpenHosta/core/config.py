from __future__ import annotations

import sys

from ..models.OpenAICompatible import Model
from ..utils.meta_prompt import EMULATE_PROMPT, Prompt

class AlwaysDefaultPolicy:
    """
    This policy always use the default prompt with the default model
    """

    def __init__(self, default_model:Model=None, default_prompt:Prompt=EMULATE_PROMPT):
        self.model = default_model
        self.prompt = default_prompt

    def set_default_model(self, new):
        if isinstance(new, Model):
            self.model = new
        else:
            sys.stderr.write("[CONFIG_ERROR] Invalid model instance.\n")

    def set_default_apiKey(self, api_key=None):
        if api_key is not None or isinstance(api_key, str):
            self.model.api_key = api_key
        else:
            sys.stderr.write("[CONFIG_ERROR] Invalid API key.")

    def get_model(self):
        return self.model

    def get_prompt(self):
        return self.prompt

DefaultModelPolicy = AlwaysDefaultPolicy()

def set_default_model(new):
    DefaultModelPolicy.set_default_model(new)


def set_default_apiKey(api_key:str=None):
    DefaultModelPolicy.set_default_apiKey(api_key)

