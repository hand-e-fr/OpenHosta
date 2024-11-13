from __future__ import annotations

import os

HOSTAPATH = "./"
PROMPTPATH = "src/prompt.json"

from .core.config import Model, DefaultManager

DefaultManager.set_default_model(
    Model(model="gpt-4o", base_url="https://api.openai.com/v1/chat/completions", api_key=os.getenv("OPENAI_API_KEY") or None)
)

from .core import config
from .exec.emulate import emulate
from .exec.example import example
from .exec.thought import thought
from .exec.thinkof import thinkof
from .utils.prompt import PromptManager
from .exec.predict.predict import predict
from .exec.predict.model_schema import ConfigModel
from .exec.predict.model import ArchitectureType
from .exec.ask import ask

all = (
    "config",
    "emulate",
    "thought",
    "example",
    "thinkof",
    "ask",
    "PromptManager",
    "predict",
    "ModelSchema",
    "ArchitectureType",
)