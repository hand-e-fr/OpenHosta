from __future__ import annotations

all = (
    "is_pydantic_enabled"
    "is_predict_enabled"
)

is_pydantic_enabled = False
try:
    import pydantic
    is_pydantic_enabled = True
except ImportError:
    is_pydantic_enabled = False

is_predict_enabled = False
try:
    import torch
    import numpy
    is_predict_enabled = True
except ImportError:
    is_predict_enabled = False
