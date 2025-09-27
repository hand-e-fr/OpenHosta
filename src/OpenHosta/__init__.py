__version__ = "3.0.0"

from .utils.import_handler import is_torch_available

from .core import config
from .core.logger import print_last_prompt
from .core.meta_prompt import MetaPrompt

from .exec.ask import ask, ask_async
from .exec.emulate import emulate, emulate_async
from .exec.closure import closure, closure_async

from .models import OpenAICompatibleModel as Model
from .models import OpenAICompatibleModel

from .core.config import DefaultModel

import os

all = (
    "config",
    "emulate",
    "Model",
    "DefaultModel"
    "OpenAICompatibleModel",
    "emulate_async",
    "closure",
    "closure_async",
    "return_type",
    "ask",
    "ask_async",
    "example",
    "thought",
    "MetaPrompt",
    "print_last_prompt",
    "generate_data",
    "generate_data_async",
    "HostaDataset",
    "SourceType"
)
