__version__ = "3.0.0"

from .core import config
from .core.logger import print_last_prompt, print_last_decoding
from .core.meta_prompt import MetaPrompt

from .exec.ask import ask, ask_async
from .exec.emulate import emulate, emulate_async
from .exec.closure import closure, closure_async

from .models import OpenAICompatibleModel as Model
from .models import OpenAICompatibleModel

from .core.config import DefaultModel, reload_dotenv

import os

all = (
    "ask",
    "ask_async",
    "emulate",
    "emulate_async",
    "closure",
    "closure_async",
    "config",
    "reload_dotenv",
    "Model",
    "DefaultModel"
    "OpenAICompatibleModel",
    "MetaPrompt",
    "print_last_prompt",
    "print_last_decoding",
)
