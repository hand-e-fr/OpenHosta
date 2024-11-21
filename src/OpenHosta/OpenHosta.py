from __future__ import annotations

from .exec.ask import ask
from .utils.meta_prompt import EMULATE_PROMPT
from .exec.thinkof import thinkof
from .exec.thought import thought
from .exec.example import example
from .exec.emulate import emulate
from .exec.generate_data import generate_data
from .exec.predict.dataset.dataset import HostaDataset, SourceType
from .core import config
from .core.config import Model, DefaultManager
from .utils.meta_prompt import print_last_prompt

import os

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
    "print_last_prompt",
    "generate_data",
    "HostaDataset",
    "SourceType"
)
