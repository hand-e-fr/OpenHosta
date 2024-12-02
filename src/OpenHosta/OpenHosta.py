from __future__ import annotations

from .core import config
from .core.config import Model, DefaultManager
from .core.checker import HostaChecker, Func

from .utils.meta_prompt import print_last_prompt
from .utils.import_handler import is_predict
from .utils.meta_prompt import EMULATE_PROMPT

from .exec.ask import ask
from .exec.thinkof import thinkof
from .exec.thought import thought
from .exec.example import example
from .exec.emulate import emulate

if is_predict:
    from .exec.generate_data import generate_data
    from .exec.predict.dataset.dataset import HostaDataset, SourceType
    from .exec.predict.predict import predict
    from .exec.predict.predict_config import PredictConfig

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
    "SourceType",
    "HostaChecker"
    "Func"
)
