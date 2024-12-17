import sys

from .config import Model

class DefaultModel:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DefaultModel, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "model"):
            self.model = None

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

    def get_default_model(self):
        return self.model

DefaultManager = DefaultModel()

def set_default_model(new):
    DefaultManager.set_default_model(new)

def set_default_apiKey(api_key=None):
    DefaultManager.set_default_apiKey(api_key)