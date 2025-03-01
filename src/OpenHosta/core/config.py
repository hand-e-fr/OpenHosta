from __future__ import annotations

import sys

from ..models.OpenAICompatible import Model
from ..utils.meta_prompt import EMULATE_PROMPT, Prompt

from typing import Tuple
from abc import ABC, abstractmethod

class ModelPolicy(ABC):
    """
    Abstract base class defining the interface for model selection policies.

    This class provides a template for implementing different strategies
    for selecting and managing AI models.
    """

    @abstractmethod
    def apply_policy(self, user_desired_model=None, prompt_data=None) -> Tuple[Model, Prompt]:
        """
        Apply the policy to select an appropriate model.

        Args:
            user_desired_model (Model, optional): The model specifically requested by the user.

        Returns:
            Model: The selected model according to the policy implementation.
        """
        pass

    @abstractmethod
    def get_model(self) -> Model:
        """
        Retrieve the current model associated with this policy.

        Returns:
            Model: The current model instance.
        """
        pass

class AlwaysDefaultPolicy(ModelPolicy):
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
    
    def apply_policy(self, desired_model=None, desired_prompt=None, prompt_data=None) -> Tuple[Model, Prompt]:

        selected_model = desired_model
        selected_prompt = desired_prompt

        if type(selected_prompt) is str:
            selected_prompt = Prompt(selected_prompt)

        if selected_model == None:
            selected_model = self.get_model()
        
        if selected_prompt == None:
            selected_prompt = self.get_prompt()

        return selected_model, selected_prompt

    def get_prompt(self):
        return self.prompt

DefaultModelPolicy = AlwaysDefaultPolicy()

def set_default_model(new):
    DefaultModelPolicy.set_default_model(new)


def set_default_apiKey(api_key:str=None):
    DefaultModelPolicy.set_default_apiKey(api_key)

