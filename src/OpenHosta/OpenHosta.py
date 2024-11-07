from __future__ import annotations

import os

HOSTAPATH = "./"
PROMPTPATH = "src/prompt.json"

from .core.config import Model, DefaultManager

DefaultManager.set_default_model(
    Model(model="gpt-4o", base_url="https://api.openai.com/v1/chat/completions", api_key=os.getenv("OPENAI_API_KEY") or None)
)

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
