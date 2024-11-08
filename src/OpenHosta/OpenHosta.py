from __future__ import annotations
from .exec.ask import ask
from .exec.predict.architecture.builtins import ArchitectureType
from .exec.predict.model_schema import ConfigModel
from .exec.predict.predict import predict
from .utils.meta_prompt import EMULATE_PROMPT
from .exec.thinkof import thinkof
from .exec.thought import thought
from .exec.example import example
from .exec.emulate import emulate
from .core import config
from .core.config import Model, DefaultManager

import os

HOSTAPATH = "./"
PROMPTPATH = "src/prompt.json"


DefaultManager.set_default_model(
    Model(model="gpt-4o", base_url="https://api.openai.com/v1/chat/completions",
          api_key=os.getenv("OPENAI_API_KEY") or None)
)


all = (
    "config",
    "emulate",
    "thought",
    "example",
    "thinkof",
    "ask",
    "EMULATE_PROMPT",
    "predict",
    "ModelSchema",
    "ArchitectureType",
)
