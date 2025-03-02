from __future__ import annotations

from .core import config
from .core.config import Model, DefaultModelPolicy
from .core.type_converter import TypeConverter, FunctionMetadata

from .core.logger import print_last_prompt, print_last_response
from .utils.import_handler import is_predict_enabled
from .utils.meta_prompt import Prompt

from .exec.ask import ask, ask_async
from .exec.thinkof import thinkof, thinkof_async, return_type
from .exec.emulate import emulate, emulate_async

from .exec.thought import thought
from .exec.example import example

if is_predict_enabled:
    from .exec.generate_data import generate_data, generate_data_async
    from .exec.predict.predict import predict, predict_async, clear_training
    from .exec.predict.dataset.dataset import HostaDataset, SourceType
    from .exec.predict.predict_config import PredictConfig
else:
    from .exec.predict.stubs import generate_data, generate_data_async
    from .exec.predict.stubs import predict, predict_async, clear_training
    from .exec.predict.stubs import HostaDataset, SourceType
    from .exec.predict.stubs import PredictConfig    

import os

DefaultModelPolicy.set_default_model(
    Model(model="gpt-4o", base_url="https://api.openai.com/v1/chat/completions")
)

all = (
    "config",
    "emulate",
    "emulate_async",
    "thinkof",
    "thinkof_async",
    "return_type",
    "ask",
    "ask_async",
    "example",
    "thought",
    "Prompt",
    "print_last_prompt",
    "print_last_response",
    "generate_data",
    "generate_data_async",
    "HostaDataset",
    "SourceType",
    "TypeConverter"
    "FunctionMetadata",
)
